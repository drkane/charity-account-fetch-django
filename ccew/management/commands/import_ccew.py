# -*- coding: utf-8 -*-
import csv
import io
import zipfile
from datetime import datetime, timedelta

import psycopg2.extras
import requests
import requests_cache
import tqdm
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction
from django.db.models.fields import BooleanField, DateField

from ccew.models import (
    Charity,
    CharityAnnualReturnHistory,
    CharityAreaOfOperation,
    CharityARPartA,
    CharityARPartB,
    CharityClassification,
    CharityEventHistory,
    CharityGoverningDocument,
    CharityOtherNames,
    CharityOtherRegulators,
    CharityPolicy,
    CharityPublishedReport,
    CharityTrustee,
)

from .create_dummy_charity import DUMMY_CHARITY_TYPE

DEFAULT_DATE_FORMAT = "%Y-%m-%d"


class Command(BaseCommand):
    help = "Import CCEW data from a zip file"

    encoding = "cp858"
    base_url = "https://ccewuksprdoneregsadata1.blob.core.windows.net/data/txt/publicextract.{}.zip"
    ccew_file_to_object = {
        "charity": Charity,
        "charity_annual_return_history": CharityAnnualReturnHistory,
        "charity_annual_return_parta": CharityARPartA,
        "charity_annual_return_partb": CharityARPartB,
        "charity_area_of_operation": CharityAreaOfOperation,
        "charity_classification": CharityClassification,
        "charity_event_history": CharityEventHistory,
        "charity_governing_document": CharityGoverningDocument,
        "charity_other_names": CharityOtherNames,
        "charity_other_regulators": CharityOtherRegulators,
        "charity_policy": CharityPolicy,
        "charity_published_report": CharityPublishedReport,
        "charity_trustee": CharityTrustee,
    }

    def logger(self, message, error=False):
        if error:
            self.stderr.write(self.style.ERROR(message))
        self.stdout.write(self.style.SUCCESS(message))

    def handle(self, *args, **options):
        self.session = requests_cache.CachedSession(
            "demo_cache.sqlite",
            expire_after=timedelta(days=1),
        )

        # ensure any demonstration charities aren't deleted
        self.demo_charities = list(
            Charity.objects.filter(charity_type=DUMMY_CHARITY_TYPE).values_list(
                "organisation_number", flat=True
            )
        )

        self.fetch_file()
        for filename, response in self.files.items():
            self.parse_file(response, filename)

    def fetch_file(self):
        self.files = {}
        for filename in self.ccew_file_to_object:
            url = self.base_url.format(filename)
            r = self.session.get(url)
            r.raise_for_status()
            self.parse_file(r, filename)

    def parse_file(self, response, filename):
        try:
            z = zipfile.ZipFile(io.BytesIO(response.content))
        except zipfile.BadZipFile:
            self.logger(response.content[0:1000])
            raise
        for f in z.infolist():
            self.logger("Opening: {}".format(f.filename))
            with z.open(f) as csvfile:
                self.process_file(csvfile, filename)
        z.close()

    def process_file(self, csvfile, filename):

        db_table = self.ccew_file_to_object.get(filename)
        date_fields = [
            f.name for f in db_table._meta.fields if isinstance(f, DateField)
        ]
        bool_fields = [
            f.name for f in db_table._meta.fields if isinstance(f, BooleanField)
        ]
        page_size = 10000

        def get_data(reader, row_count=None):
            for k, row in tqdm.tqdm(enumerate(reader)):
                row = self.clean_fields(row, date_fields, bool_fields)
                if row_count and row_count != len(row):
                    self.logger(row)
                    raise ValueError(
                        "Incorrect number of rows (expected {} and got {})".format(
                            row_count,
                            len(row),
                        )
                    )
                yield list(row.values())

        def get_data_chunks(reader, row_count=None):
            rows = []
            for row in get_data(reader, row_count):
                rows.append(tuple(row))
                if len(rows) == page_size:
                    for r in rows:
                        yield r
                    rows = []
            if rows:
                for r in rows:
                    yield r

        with connection.cursor() as cursor, transaction.atomic():
            reader = csv.DictReader(
                io.TextIOWrapper(csvfile, encoding="utf8"),
                delimiter="\t",
                escapechar="\\",
                quoting=csv.QUOTE_NONE,
            )
            self.logger(
                "Deleting existing records [{}]".format(db_table._meta.db_table)
            )
            columns = tuple(f.name for f in db_table._meta.fields)
            if "organisation_number" in columns:
                deleted, _ = db_table.objects.exclude(
                    organisation_number__in=self.demo_charities
                ).delete()
            elif "charity" in columns:
                deleted, _ = db_table.objects.exclude(
                    charity_id__in=self.demo_charities
                ).delete()
            self.logger(
                "Deleted {:,.0f} existing records [{}]".format(
                    deleted, db_table._meta.db_table
                )
            )

            # reset the sequence
            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [db_table])
            for sql in sequence_sql:
                cursor.execute(sql)

            self.logger("Starting table insert [{}]".format(db_table._meta.db_table))
            fields = list(reader.fieldnames)
            statement = (
                """INSERT INTO "{table}" ("{fields}") VALUES {placeholder};""".format(
                    table=db_table._meta.db_table,
                    fields='", "'.join(fields),
                    placeholder="(" + ", ".join(["%s" for f in fields]) + ")"
                    if connection.vendor == "sqlite"
                    else "%s",
                )
            )
            if connection.vendor == "postgresql":
                psycopg2.extras.execute_values(
                    cursor,
                    statement,
                    get_data(reader, len(reader.fieldnames)),
                    page_size=page_size,
                )
            else:
                cursor.executemany(
                    statement,
                    get_data_chunks(reader, len(reader.fieldnames)),
                )
            self.logger("Finished table insert [{}]".format(db_table._meta.db_table))

    def clean_fields(self, record, date_fields=[], bool_fields=[]):
        for f in record.keys():
            # clean blank values
            if record[f] == "":
                record[f] = None

            # clean date fields
            elif f in date_fields and isinstance(record[f], str):
                try:
                    if record.get(f):
                        record[f] = datetime.strptime(
                            record.get(f)[0:10].strip(), "%Y-%m-%d"
                        ).date()
                except ValueError:
                    record[f] = None

            # clean boolean fields
            elif f in bool_fields:
                if isinstance(record[f], str):
                    val = record[f].lower().strip()
                    if val in ["f", "false", "no", "0", "n"]:
                        record[f] = False
                    elif val in ["t", "true", "yes", "1", "y"]:
                        record[f] = True

            # strip string fields
            elif isinstance(record[f], str):
                record[f] = record[f].strip().replace("\x00", "")
        return record

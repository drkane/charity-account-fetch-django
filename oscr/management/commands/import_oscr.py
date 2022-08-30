from operator import index
from django.core.management.base import BaseCommand
import requests_cache
from datetime import datetime, timedelta, date
import csv
import io
from django.utils.text import slugify
from django.db import connection, transaction
from oscr.models import Charity, CharityFinancialYear
import psycopg2.extras
import zipfile
import re


fy_fields = list(f.name for f in CharityFinancialYear._meta.fields if f.name != "id")
char_fields = list(f.name for f in Charity._meta.fields if f.name != "id")
insolvency_regex = re.compile(r"\(?subject to insolvency proceedings\)?", re.IGNORECASE)


class Command(BaseCommand):
    help = "Import OSCR data from a zip file"

    base_urls = (
        "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityFormerRegDownload",
        "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityRegDownload",
        "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/Charity5YearsRegDownload",
    )

    def logger(self, message, error=False):
        if error:
            self.stderr.write(self.style.ERROR(message))
        self.stdout.write(self.style.SUCCESS(message))

    def handle(self, *args, **options):
        self.session = requests_cache.CachedSession(
            "demo_cache.sqlite",
            expire_after=timedelta(days=1),
        )

        self.charities = {}
        self.financial_years = {}

        self.fetch_file()

    def fetch_file(self):
        self.files = {}
        for url in self.base_urls:
            response = self.session.get(url)
            response.raise_for_status()

            try:
                z = zipfile.ZipFile(io.BytesIO(response.content))
            except zipfile.BadZipFile:
                self.logger(response.content[0:1000])
                raise
            for file_ in z.infolist():
                self.logger("Opening: {}".format(file_.filename))
                with z.open(file_) as csvfile:
                    reader = csv.DictReader(io.TextIOWrapper(csvfile, encoding="utf8"))
                    rowcount = 0
                    for row in reader:
                        rowcount += 1
                        self.add_charity(row)
            z.close()
        self.save_charities()

    def add_charity(self, record):
        record = {
            slugify(k.strip().replace("/", "_")).replace("-", "_"): v.strip()
            if v
            not in (
                "",
                "-",
                "-, -",
            )
            else None
            for k, v in record.items()
            if k
        }

        # array fields
        for k in [
            "purposes",
            "beneficiaries",
            "activities",
        ]:
            if record.get(k):
                reader = csv.reader([record[k]], delimiter=",", quotechar="'")
                record[k] = list(next(reader))

        # date fields
        for k, format_ in [
            ("registered_date", "%d/%m/%Y %H:%M"),
            ("ceased_date", "%d/%m/%Y %H:%M"),
            ("year_end", "%d/%m/%Y"),
            ("date_annual_return_received", "%d/%m/%Y"),
            ("next_year_end_date", "%d/%m/%Y"),
        ]:
            if record.get(k):
                record[k] = datetime.strptime(record[k], format_).date()
                if record[k] == date(1970, 1, 1):
                    record[k] = None

        # int fields
        for k in [
            "mailing_cycle",
            "most_recent_year_income",
            "most_recent_year_expenditure",
            "donations_and_legacies_income",
            "charitable_activities_income",
            "other_trading_activities_income",
            "investments_income",
            "other_income",
            "raising_funds_spending",
            "charitable_activities_spending",
            "other_spending",
        ]:
            if isinstance(record.get(k), str):
                record[k] = int(record[k])

        # website field
        if record.get("website") and not record.get("website").startswith("http"):
            record["website"] = "http://" + record["website"]

        # postcode field
        if record.get("postcode") == "XX0 0XX":
            record["postcode"] = None
        if record.get("postcode"):
            record["postcode"] = record["postcode"].upper()

        # add charity financial year to list
        if record["year_end"]:
            self.financial_years[(record["charity_number"], record["year_end"])] = {
                k: v for k, v in record.items() if k in fy_fields
            }

        # replace "subject to insolvency proceedings" in charity name
        if insolvency_regex.search(record["charity_name"]):
            record["charity_name"] = re.sub(
                r"\W+$", "", insolvency_regex.sub("", record["charity_name"])
            ).strip()
            if record["notes"]:
                record["notes"] += ". Subject to insolvency proceedings."
            else:
                record["notes"] = "Subject to insolvency proceedings."

        # check whether we have seen this charity before
        if record["charity_number"] in self.charities:
            latest_data = self.charities[record["charity_number"]]
            if (
                latest_data["year_end"]
                and latest_data["year_end"] >= record["year_end"]
            ):
                return
        self.charities[record["charity_number"]] = record

    def save_charities(self):
        page_size = 10000
        with connection.cursor() as cursor, transaction.atomic():

            # delete existing charities
            Charity.objects.all().delete()

            # insert new charities
            statement = """INSERT INTO "{table}" ("{fields}") VALUES %s;""".format(
                table=Charity._meta.db_table,
                fields='", "'.join(char_fields),
            )
            psycopg2.extras.execute_values(
                cursor,
                statement,
                [[c.get(f) for f in char_fields] for c in self.charities.values()],
                page_size=page_size,
            )
            self.logger("Finished table insert [{}]".format(Charity._meta.db_table))

            # insert financial years
            statement = """INSERT INTO "{table}" ("{fields}") VALUES %s
                    ON CONFLICT(charity_number, year_end) DO UPDATE
                    SET {on_conflict}""".format(
                table=CharityFinancialYear._meta.db_table,
                fields='", "'.join(fy_fields),
                on_conflict=", ".join(
                    (
                        '"{}" = excluded."{}"'.format(f, f)
                        for f in fy_fields
                        if f not in ("charity_number", "year_end")
                    )
                ),
            )
            psycopg2.extras.execute_values(
                cursor,
                statement,
                [[c.get(f) for f in fy_fields] for c in self.financial_years.values()],
                page_size=page_size,
            )
            self.logger(
                "Finished table insert [{}]".format(CharityFinancialYear._meta.db_table)
            )

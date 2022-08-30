import csv
import io
from datetime import datetime, timedelta

import psycopg2.extras
import requests_cache
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils.text import slugify

from ccni.models import Charity


class Command(BaseCommand):
    help = "Import CCEW data from a zip file"

    base_url = "https://www.charitycommissionni.org.uk/umbraco/api/charityApi/ExportSearchResultsToCsv/?include=Linked&include=Removed"

    def logger(self, message, error=False):
        if error:
            self.stderr.write(self.style.ERROR(message))
        self.stdout.write(self.style.SUCCESS(message))

    def handle(self, *args, **options):
        self.session = requests_cache.CachedSession(
            "demo_cache.sqlite",
            expire_after=timedelta(days=1),
        )

        self.charities = []

        self.fetch_file()

    def fetch_file(self):
        self.files = {}
        r = self.session.get(self.base_url)
        r.raise_for_status()

        file = io.StringIO(r.text)
        reader = csv.DictReader(file)
        for k, row in enumerate(reader):
            self.add_charity(row)
        self.save_charities()

    def add_charity(self, record):
        record = {
            slugify(k).replace("-", "_"): v if v != "" else None
            for k, v in record.items()
            if k
        }

        # array fields
        for k in [
            "what_the_charity_does",
            "who_the_charity_helps",
            "how_the_charity_works",
        ]:
            record[k] = record.get(k, "").split(",")

        # date fields
        for k, format_ in [
            ("date_registered", "%d/%m/%Y"),
            ("date_for_financial_year_ending", "%d %B %Y"),
        ]:
            record[k] = datetime.strptime(record[k], format_)

        # int fields
        for k in [
            "reg_charity_number",
            "sub_charity_number",
            "total_income",
            "total_spending",
            "charitable_spending",
            "income_generation_and_governance",
            "retained_for_future_use",
        ]:
            record[k] = int(record[k])

        # company number field
        if record.get("company_number") == "0":
            record["company_number"] = None
        if record.get("company_number"):
            record["company_number"] = "NI" + record["company_number"].zfill(6)

        # website field
        if record.get("website") and not record.get("website").startswith("http"):
            record["website"] = "http://" + record["website"]
        self.charities.append(record)

    def save_charities(self):
        page_size = 10000
        with connection.cursor() as cursor, transaction.atomic():

            # delete existing charities
            Charity.objects.all().delete()

            # get field names
            fields = list(f.name for f in Charity._meta.fields if f.name != "id")

            # insert new charities
            statement = (
                """INSERT INTO "{table}" ("{fields}") VALUES {placeholder};""".format(
                    table=Charity._meta.db_table,
                    fields='", "'.join(fields),
                    placeholder="(" + ", ".join(["%s" for f in fields]) + ")"
                    if connection.vendor == "sqlite"
                    else "%s",
                )
            )
            psycopg2.extras.execute_values(
                cursor,
                statement,
                [[c.get(f) for f in fields] for c in self.charities],
                page_size=page_size,
            )
            self.logger("Finished table insert [{}]".format(Charity._meta.db_table))

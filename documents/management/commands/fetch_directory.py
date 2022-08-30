import argparse
import datetime
import os

from django.core.management.base import BaseCommand
from django_q.tasks import async_task

from documents.fetch import document_from_file
from documents.models import Tag


def parse_financial_year_end(s):
    if s in ["all", "latest"]:
        return s
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


class Command(BaseCommand):
    help = "Import records from a directory. Filenames should be in the format ORGID_YYYYMMDD.pdf, eg GB-CHC-1234567_20200101.pdf"

    def add_arguments(self, parser):
        parser.add_argument("directory", type=str)
        parser.add_argument(
            "--tags",
            "-t",
            nargs="+",
            default=[],
        )
        parser.add_argument("--test", action=argparse.BooleanOptionalAction)

    def handle(self, *args, **options):
        tags = list(
            Tag.objects.get_or_create(
                slug=Tag._meta.get_field("slug").slugify(tag), defaults=dict(name=tag)
            )[0]
            for tag in options["tags"]
        )
        files_found = 0
        for dirpath, dirnames, filenames in os.walk(options["directory"]):
            for filename in filenames:
                if options["test"] and files_found > 10:
                    break
                if not filename.endswith(".pdf"):
                    continue

                try:
                    org_id, financial_year_end = filename[:-4].split("_")
                    financial_year_end = datetime.datetime.strptime(
                        financial_year_end, "%Y%m%d"
                    ).date()
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"could not parse {filename}"))
                    continue

                _ = async_task(
                    document_from_file,
                    org_id,
                    financial_year_end,
                    os.path.join(dirpath, filename),
                    tags=tags,
                )
                files_found += 1

        self.stdout.write(self.style.SUCCESS(f"Found {files_found:.0f} files"))

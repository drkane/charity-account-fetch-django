import datetime

from django.core.management.base import BaseCommand
from django_q.tasks import async_task

from documents.fetch import fetch_documents_for_charity
from documents.models import Tag


def parse_financial_year_end(s):
    if s in ["all", "latest"]:
        return s
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


class Command(BaseCommand):
    help = "Transfer charity records to table"

    def add_arguments(self, parser):
        parser.add_argument("org_id", type=str)
        parser.add_argument(
            "--financial-year-end",
            "-f",
            type=parse_financial_year_end,
            default="latest",
        )
        parser.add_argument(
            "--tags",
            "-t",
            nargs="+",
            default=[],
        )

    def handle(self, *args, **options):
        tags = list(
            Tag.objects.get_or_create(
                slug=Tag._meta.get_field("slug").slugify(tag), defaults=dict(name=tag)
            )[0]
            for tag in options["tags"]
        )
        task_id = async_task(
            fetch_documents_for_charity,
            options["org_id"],
            financial_year_end=options["financial_year_end"],
            tags=tags,
        )
        self.stdout.write(self.style.SUCCESS(f"Task {task_id} started"))

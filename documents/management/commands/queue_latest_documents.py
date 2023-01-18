from django.core.management.base import BaseCommand
from django.db.models import F
from django_q.tasks import async_task

from documents.fetch import fetch_documents_for_charity
from documents.models import CharityFinancialYear, FetchGroup, Regulators


class Command(BaseCommand):
    help = "Add the latest documents for largest charities to the queue"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            "-n",
            type=int,
            default=50,
            help="Number of documents to fetch",
        )

    def handle(self, *args, **options):
        n = min(options["number"], 1000)

        task_group = FetchGroup.objects.create()

        documents = CharityFinancialYear.objects.filter(
            documents__isnull=True,
            income__gt=25000,
            charity__source=Regulators.CCEW,
            document_submitted__isnull=False,
        ).order_by(F("income").desc(nulls_last=True))[:n]
        self.stdout.write(str(documents.query))
        for record in documents:
            task_id = async_task(
                fetch_documents_for_charity,
                record.charity.org_id,
                record.financial_year_end,
                group=task_group.id,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Document {record} added to queue (task id: {task_id})"
                )
            )

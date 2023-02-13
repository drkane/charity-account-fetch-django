from datetime import date as Date

from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone
from django_q.tasks import async_task

from documents.fetch import fetch_documents_for_charity
from documents.models import (
    CharityFinancialYear,
    DocumentStatus,
    FetchGroup,
    Regulators,
)


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
        parser.add_argument(
            "--earliest",
            "-e",
            type=Date,
            default=Date(2016, 1, 1),
            help="Earliest year to fetch",
        )

    def handle(self, *args, **options):
        n = min(options["number"], 10_000)

        task_group = FetchGroup.objects.create()

        documents = CharityFinancialYear.objects.filter(
            documents__isnull=True,
            status__isnull=True,
            income__gt=25000,
            charity__source=Regulators.CCEW,
            document_submitted__isnull=False,
            charity__date_removed__isnull=True,
            financial_year_end__gt=options["earliest"],
        ).order_by(
            F("financial_year_end__year").asc(nulls_last=True),
            F("income").desc(nulls_last=True),
        )[
            :n
        ]

        for record in documents:
            task_id = async_task(
                fetch_documents_for_charity,
                record.charity.org_id,
                record.financial_year_end,
                group=task_group.id,
            )
            record.task_id = task_id
            record.status = DocumentStatus.PENDING
            record.last_document_fetch_started = timezone.now()
            record.task_groups.add(task_group)
            record.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Document {record} added to queue (task id: {task_id})"
                )
            )

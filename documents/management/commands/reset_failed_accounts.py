from django.core.management.base import BaseCommand

from documents.models import (
    CharityFinancialYear,
    DocumentStatus,
    Regulators,
)

FAILED_STATUS = "Accounts not found. Available accounts: "


class Command(BaseCommand):
    help = "Reset failed account fetches that meet specific criteria"

    def handle(self, *args, **options):
        documents = CharityFinancialYear.objects.filter(
            status=DocumentStatus.FAILED,
            status_notes=FAILED_STATUS,
            last_document_fetch_started__isnull=False,
            charity__source=Regulators.CCEW,
        ).update(
            status=None,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Reset status of {documents:,.0f} documents that failed"
            )
        )

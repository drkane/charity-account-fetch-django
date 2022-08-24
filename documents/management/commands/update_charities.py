from django.core.management.base import BaseCommand
from django.db import connection, transaction

UPDATE_SQL = {
    "Deleting existing CCEW records": """
            delete from documents_charity
            where lower(source) = 'ccew'
            """,
    "Insert updated CCEW records": """
            insert into documents_charity 
            select 'GB-CHC-' || registered_charity_number as org_id,
                'CCEW' as source,
                "charity_name" as name,
                date_of_registration as date_registered,
                date_of_removal as date_removed
            from ccew_charity
            where linked_charity_number = 0
    """,
    "Insert financial records": """
        insert into documents_charityfinancialyear (
        financial_year_end, document_due, document_submitted, income, expenditure, charity_id)
        select distinct on (registered_charity_number, fin_period_end_date)
            fin_period_end_date as financial_year_end,
            reporting_due_date as document_due,
            date_accounts_received as document_submitted,
            total_gross_income as income,
            total_gross_expenditure as expenditure,
            'GB-CHC-' || registered_charity_number as charity_id
        from ccew_charityannualreturnhistory cc 
        WHERE true
        ON CONFLICT(charity_id, financial_year_end) DO UPDATE
        SET document_due = excluded.document_due,
            document_submitted = excluded.document_submitted,
            income = excluded.income,
            expenditure = excluded.expenditure
    """,
}


class Command(BaseCommand):
    help = "Transfer charity records to table"

    def handle(self, *args, **options):
        with connection.cursor() as cursor, transaction.atomic():
            for title, sql in UPDATE_SQL.items():
                self.stdout.write(f"SQL: {title}")
                cursor.execute(sql)
                self.stdout.write(self.style.SUCCESS(f"SQL COMPLETED: {title}"))
                if cursor.rowcount:
                    self.stdout.write(
                        self.style.SUCCESS(f"{cursor.rowcount} rows affected")
                    )

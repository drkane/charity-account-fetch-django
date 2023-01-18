from django.core.management.base import BaseCommand
from django.db import connection, transaction

UPDATE_SQL = {
    "Insert updated CCEW records": """
        insert into documents_charity
        select 'GB-CHC-' || registered_charity_number as org_id,
            'CCEW' as source,
            "charity_name" as name,
            date_of_registration as date_registered,
            date_of_removal as date_removed,
            NOW() as created_at,
            NOW() as updated_at
        from ccew_charity
        where linked_charity_number = 0
        ON CONFLICT(org_id) DO UPDATE
        SET name = excluded.name,
            date_registered = excluded.date_registered,
            date_removed = excluded.date_removed,
            created_at = documents_charity.created_at,
            updated_at = excluded.updated_at
    """,
    "Insert CCEW financial records": """
        insert into documents_charityfinancialyear (
        financial_year_end, document_due, document_submitted, income, expenditure, charity_id, created_at, updated_at)
        select distinct on (registered_charity_number, fin_period_end_date)
            fin_period_end_date as financial_year_end,
            reporting_due_date as document_due,
            date_accounts_received as document_submitted,
            total_gross_income as income,
            total_gross_expenditure as expenditure,
            'GB-CHC-' || registered_charity_number as charity_id,
            NOW() as created_at,
            NOW() as updated_at
        from ccew_charityannualreturnhistory cc
        WHERE true
        ON CONFLICT(charity_id, financial_year_end) DO UPDATE
        SET document_due = excluded.document_due,
            document_submitted = excluded.document_submitted,
            income = excluded.income,
            expenditure = excluded.expenditure
    """,
    "Insert updated CCNI records": """
        insert into documents_charity
        select 'GB-NIC-' || reg_charity_number as org_id,
            'CCNI' as source,
            "charity_name" as name,
            date_registered as date_registered,
            null as date_removed,
            NOW() as created_at,
            NOW() as updated_at
        from ccni_charity
        where sub_charity_number = 0
        ON CONFLICT(org_id) DO UPDATE
        SET name = excluded.name,
            date_registered = excluded.date_registered,
            date_removed = excluded.date_removed,
            created_at = documents_charity.created_at,
            updated_at = excluded.updated_at
    """,
    "Insert CCNI financial records": """
        insert into documents_charityfinancialyear (
        financial_year_end, income, expenditure, charity_id, created_at, updated_at)
        select date_for_financial_year_ending as financial_year_end,
            total_income as income,
            total_spending as expenditure,
            'GB-NIC-' || reg_charity_number as charity_id,
            NOW() as created_at,
            NOW() as updated_at
        from ccni_charity
        where total_income <> 0 or total_spending <> 0
        ON CONFLICT(charity_id, financial_year_end) DO UPDATE
        SET income = excluded.income,
            expenditure = excluded.expenditure
    """,
    "Insert updated OSCR records": """
        insert into documents_charity 
        select 'GB-SC-' || charity_number as org_id,
            'OSCR' as source,
            "charity_name" as name,
            registered_date as date_registered,
            ceased_date as date_removed,
            NOW() as created_at,
            NOW() as updated_at
        from oscr_charity
        ON CONFLICT(org_id) DO UPDATE
        SET name = excluded.name,
            date_registered = excluded.date_registered,
            date_removed = excluded.date_removed,
            created_at = documents_charity.created_at,
            updated_at = excluded.updated_at
    """,
    "Insert OSCR financial records": """
        insert into documents_charityfinancialyear (
        financial_year_end, document_submitted, income, expenditure, charity_id, created_at, updated_at)
        select year_end as financial_year_end,
            date_annual_return_received as document_submitted,
            most_recent_year_income as income,
            most_recent_year_expenditure as expenditure,
            'GB-SC-' || charity_id as charity_id,
            NOW() as created_at,
            NOW() as updated_at
        from oscr_charityfinancialyear
        ON CONFLICT(charity_id, financial_year_end) DO UPDATE
        SET income = excluded.income,
            expenditure = excluded.expenditure,
            document_submitted = excluded.document_submitted
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

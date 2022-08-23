from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker

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

from ._charity_provider import CharityProvider

DUMMY_CHARITY_TYPE = "Demonstration Charity"


class Command(BaseCommand):
    help = "Create a dummy charity for testing/sample purposes"

    def handle(self, *args, **options):
        fake = Faker("en_GB")
        fake.add_provider(CharityProvider)
        charity_name = fake.charity_name()
        extract_date = date.today()

        charity, created = Charity.objects.update_or_create(
            registered_charity_number=123456,
            defaults=dict(
                date_of_extract=extract_date,  #  models.DateField(
                organisation_number=123456,  #  models.IntegerField(
                # registered_charity_number="", #  models.IntegerField(
                linked_charity_number=0,  #  models.IntegerField(
                charity_name=charity_name,  #  models.CharField(
                charity_type=DUMMY_CHARITY_TYPE,  #  models.CharField(
                charity_registration_status="Registered",  #  models.CharField(
                date_of_registration=date(2005, 1, 1),  #  models.DateField(
                date_of_removal=None,  #  models.DateField(
                charity_reporting_status="Submission Received",  #  models.CharField(
                latest_acc_fin_period_start_date=date(2020, 4, 1),  #  models.DateField(
                latest_acc_fin_period_end_date=date(2021, 3, 31),  #  models.DateField(
                latest_income=1_500_340,  #  models.FloatField(
                latest_expenditure=1_450_000,  #  models.FloatField(
                charity_contact_address1=fake.street_address(),  #  models.CharField(
                charity_contact_address2=fake.city(),  #  models.CharField(
                charity_contact_address3="",  #  models.CharField(
                charity_contact_address4="",  #  models.CharField(
                charity_contact_address5="",  #  models.CharField(
                charity_contact_postcode=fake.postcode(),  #  models.CharField(
                charity_contact_phone=fake.phone_number(),  #  models.CharField(
                charity_contact_email=f"{slugify(charity_name)}@example.com",  #  models.CharField(
                charity_contact_web=f"https://www.example.com/{slugify(charity_name)}",  #  models.CharField(
                charity_company_registration_number=fake.company_number(),  #  models.CharField(
                charity_insolvent=False,  #  models.BooleanField(
                charity_in_administration=False,  #  models.BooleanField(
                charity_previously_excepted=False,  #  models.BooleanField(
                charity_is_cdf_or_cif=None,  #  models.CharField(
                charity_is_cio=False,  #  models.BooleanField(
                cio_is_dissolved=False,  #  models.BooleanField(
                date_cio_dissolution_notice=None,  #  models.DateField(
                charity_activities="",  #  models.TextField(
                charity_gift_aid=True,  #  models.BooleanField(
                charity_has_land=True,  #  models.BooleanField(
            ),
        )
        self.stdout.write(self.style.SUCCESS(f"Created charity: {charity_name}"))

        # create dummy trustee names
        CharityTrustee.objects.filter(charity=charity).delete()
        trustees = []
        for i in range(fake.random_int(5, 10)):
            trustees.append(
                CharityTrustee.objects.create(
                    charity=charity,
                    date_of_extract=extract_date,
                    registered_charity_number=charity.registered_charity_number,
                    linked_charity_number=charity.linked_charity_number,
                    trustee_name=fake.name(),
                    trustee_id=fake.random_number(digits=6),
                    trustee_is_chair=i == 0,
                    individual_or_organisation=CharityTrustee.IndividualOrOrganisation.INDIVIDUAL,
                )
            )
        self.stdout.write(self.style.SUCCESS(f"Added {len(trustees)} trustees"))

        # remove any existing financial data
        CharityAnnualReturnHistory.objects.filter(charity=charity).delete()
        CharityARPartA.objects.filter(charity=charity).delete()
        CharityARPartB.objects.filter(charity=charity).delete()

        # create three financial years
        current_year = date.today().year
        for i in range(3):
            fye = date(current_year - i, 3, 31)
            fys = fye + relativedelta(years=-1, days=1)
            income = fake.random_int(700_000, 1_500_000)
            expenditure = int(income * 0.8)
            ar_cycle = f"AR{str(fye.year)[2:]}"

            # create annual return history
            CharityAnnualReturnHistory.objects.create(
                charity=charity,
                date_of_extract=extract_date,
                registered_charity_number=charity.registered_charity_number,
                fin_period_start_date=fys,
                fin_period_end_date=fye,
                ar_cycle_reference=ar_cycle,
                reporting_due_date=fye + relativedelta(months=10),
                date_annual_return_received=fye + relativedelta(months=8),
                date_accounts_received=fye + relativedelta(months=8),
                total_gross_income=income,
                total_gross_expenditure=expenditure,
                accounts_qualified=None,
                suppression_ind=0,
                suppression_type=None,
            )

            # add AR Part A
            CharityARPartA.objects.create(
                charity=charity,
                date_of_extract=extract_date,
                registered_charity_number=charity.registered_charity_number,
                latest_fin_period_submitted_ind=i == 0,
                fin_period_order_number=i + 1,
                ar_cycle_reference=ar_cycle,
                fin_period_start_date=fys,
                fin_period_end_date=fye,
                ar_due_date=fye + relativedelta(months=10),
                ar_received_date=fye + relativedelta(months=8),
                total_gross_income=income,
                total_gross_expenditure=expenditure,
                charity_raises_funds_from_public=True,
                charity_professional_fundraiser=False,
                charity_agreement_professional_fundraiser=False,
                charity_commercial_participator=False,
                charity_agreement_commerical_participator=False,
                grant_making_is_main_activity=False,
                charity_receives_govt_funding_contracts=False,
                count_govt_contracts=0,
                charity_receives_govt_funding_grants=True,
                count_govt_grants=1,
                income_from_government_contracts=0,
                income_from_government_grants=fake.random_int(100, income),
                charity_has_trading_subsidiary=False,
                trustee_also_director_of_subsidiary=False,
                does_trustee_receive_any_benefit=False,
                trustee_payments_acting_as_trustee=False,
                trustee_receives_payments_services=False,
                trustee_receives_other_benefit=False,
                trustee_resigned_employment=False,
                employees_salary_over_60k=0,
                count_salary_band_60001_70000=0,
                count_salary_band_70001_80000=0,
                count_salary_band_80001_90000=0,
                count_salary_band_90001_100000=0,
                count_salary_band_100001_110000=0,
                count_salary_band_110001_120000=0,
                count_salary_band_120001_130000=0,
                count_salary_band_130001_140000=0,
                count_salary_band_140001_150000=0,
                count_salary_band_150001_200000=0,
                count_salary_band_200001_250000=0,
                count_salary_band_250001_300000=0,
                count_salary_band_300001_350000=0,
                count_salary_band_350001_400000=0,
                count_salary_band_400001_450000=0,
                count_salary_band_450001_500000=0,
                count_salary_band_over_500000=0,
                count_volunteers=fake.random_int(50, 1_000),
            )
            self.stdout.write(self.style.SUCCESS(f"Added financial year: {fye}"))

            charitable_activities = fake.random_int(70, 80) / 100
            donations = fake.random_int(10, 20) / 100
            other_trading_activities = fake.random_int(1, 5) / 100
            investments = 1 - (
                charitable_activities + donations + other_trading_activities
            )
            expenditure_charitable_activities = fake.random_int(70, 80) / 100
            assets = fake.random_int(1_000_000, 5_000_000)
            restricted = fake.random_int(20, 40) / 100
            staff = int(expenditure / 45_000)

            CharityARPartB.objects.create(
                charity=charity,
                date_of_extract=extract_date,
                registered_charity_number=charity.registered_charity_number,
                latest_fin_period_submitted_ind=i == 0,
                fin_period_order_number=i + 1,
                ar_cycle_reference=ar_cycle,
                fin_period_start_date=fys,
                fin_period_end_date=fye,
                ar_due_date=fye + relativedelta(months=10),
                ar_received_date=fye + relativedelta(months=8),
                income_donations_and_legacies=donations * income,
                income_charitable_activities=charitable_activities * income,
                income_other_trading_activities=other_trading_activities * income,
                income_investments=investments * income,
                income_other=0,
                income_total_income_and_endowments=income,
                income_legacies=donations * income * 0.1,
                income_endowments=0,
                expenditure_raising_funds=expenditure
                * (1 - expenditure_charitable_activities),
                expenditure_charitable_expenditure=expenditure
                * expenditure_charitable_activities,
                expenditure_other=0,
                expenditure_total=expenditure,
                expenditure_investment_management=0,
                expenditure_grants_institution=0,
                expenditure_governance=0,
                expenditure_support_costs=0,
                expenditure_depreciation=0,
                gain_loss_investment=0,
                gain_loss_pension_fund=0,
                gain_loss_revaluation_fixed_investment=0,
                gain_loss_other=0,
                reserves=assets * 0.8,
                assets_total_fixed=0,
                assets_own_use=0,
                assets_long_term_investment=0,
                defined_benefit_pension_scheme=0,
                assets_other_assets=0,
                assets_total_liabilities=0,
                assets_current_investment=0,
                assets_total_assets_and_liabilities=0,
                creditors_one_year_total_current=0,
                creditors_falling_due_after_one_year=0,
                assets_cash=0,
                funds_endowment=0,
                funds_unrestricted=assets * (1 - restricted),
                funds_restricted=assets * restricted,
                funds_total=assets,
                count_employees=staff,
                charity_only_accounts=False,
                consolidated_accounts=True,
            )

        # remove any existing classifcation and area data
        CharityClassification.objects.filter(charity=charity).delete()
        CharityAreaOfOperation.objects.filter(charity=charity).delete()

        # add classification data
        cats_added = []
        for i in CharityClassification.ClassificationType:
            existing_choices = (
                CharityClassification.objects.filter(classification_type=i)
                .values_list("classification_code", "classification_description")
                .distinct()
            )
            for code, description in fake.random_elements(
                list(existing_choices),
                length=fake.random_int(2, 5),
                unique=True,
            ):
                cats_added.append(
                    CharityClassification.objects.create(
                        date_of_extract=extract_date,
                        charity=charity,
                        registered_charity_number=charity.registered_charity_number,
                        linked_charity_number=charity.linked_charity_number,
                        classification_code=code,
                        classification_type=i,
                        classification_description=description,
                    )
                )
        self.stdout.write(
            self.style.SUCCESS(f"Added {len(cats_added)} charity classifications")
        )

        # add area of operation data
        existing_areas = list(
            CharityAreaOfOperation.objects.filter(
                geographic_area_type="Local Authority"
            )
            .values_list("geographic_area_description", flat=True)
            .distinct()
        )
        areas = [
            CharityAreaOfOperation.objects.create(
                date_of_extract=extract_date,
                charity=charity,
                registered_charity_number=charity.registered_charity_number,
                linked_charity_number=charity.linked_charity_number,
                geographic_area_type="Local Authority",
                geographic_area_description=area,
                parent_geographic_area_type=None,
                parent_geographic_area_description=None,
                welsh_ind=False,
            )
            for area in fake.random_elements(
                existing_areas,
                length=fake.random_int(2, 5),
                unique=True,
            )
        ]
        self.stdout.write(self.style.SUCCESS(f"Added {len(areas)} areas of operation"))

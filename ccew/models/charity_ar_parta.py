from django.db import models

from .charity import Charity


class CharityARPartA(models.Model):
    date_of_extract = models.DateField(
        null=True,
        blank=True,
        help_text="The date that the extract was taken from the main dataset.",
    )
    charity = models.ForeignKey(
        Charity,
        db_column="organisation_number",
        to_field="organisation_number",
        on_delete=models.CASCADE,
        help_text="The organisation number for the charity. This is the index value for the charity.",
        related_name="annual_return_part_a",
    )
    registered_charity_number = models.IntegerField(
        db_index=True,
        help_text="The registration number of the registered organisation allocated by the Commission. Note that a main charity and all its linked charities will share the same registered_charity_number.",
    )
    latest_fin_period_submitted_ind = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates whether the financial data on this line relates to the latest financial data submitted by the charity. (True or False)",
    )
    fin_period_order_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="A field to aid ordering of the financial data for each charity. (1=Most recent data in the table, 5=Least recent data in the table)",
    )
    ar_cycle_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The annual return cycle to which the submission details relate.",
    )
    fin_period_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="The start date of the financial period which is detailed for the charity.",
    )
    fin_period_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="The end date of the financial period which is detailed for the charity.",
    )
    ar_due_date = models.DateField(
        null=True,
        blank=True,
        help_text="The due date of the annual return which is detailed for the charity.",
    )
    ar_received_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date the annual return was received for the financial period which is detailed for the charity.",
    )
    total_gross_income = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The total gross income reported on Part A of the annual return for the financial period detailed.",
    )
    total_gross_expenditure = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The total gross expenditure reported on Part A of the annual return for the financial period detailed.",
    )
    charity_raises_funds_from_public = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the charity raised funds from the public for the financial period which is detailed for the charity. (True, False or NULL)",
    )
    charity_professional_fundraiser = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the charity worked with professional fundraisers for the financial period which is detailed for the charity. (True, False or NULL)",
    )
    charity_agreement_professional_fundraiser = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the charity had an agreement with its professional fundraisers for the financial period which is detailed. (True, False or NULL)",
    )
    charity_commercial_participator = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the charity worked with commercial participators for the financial period detailed. (True, False or NULL)",
    )
    charity_agreement_commerical_participator = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the charity had an agreement with its commercial participators for the financial period detailed. (True, False or NULL)",
    )
    grant_making_is_main_activity = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if grant making was the main way the charity carried out its purposes for the financial period detailed. (True, False or NULL)",
    )
    charity_receives_govt_funding_contracts = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the charity received any income from government contracts for the financial period detailed. (True, False or NULL)",
    )
    count_govt_contracts = models.IntegerField(
        null=True,
        blank=True,
        help_text="The number of government contracts the charity had for the financial period detailed.",
    )
    charity_receives_govt_funding_grants = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the charity received any income from government grants for the financial period detailed. (True, False or NULL)",
    )
    count_govt_grants = models.IntegerField(
        null=True,
        blank=True,
        help_text="The number of government grants the charity received for the financial period detailed.",
    )
    income_from_government_contracts = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The income the charity received from government contracts for the financial period detailed.",
    )
    income_from_government_grants = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The income the charity received from government grants for the financial period detailed.",
    )
    charity_has_trading_subsidiary = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the charity had a trading subsidiary for the financial period detailed. (True, False or NULL)",
    )
    trustee_also_director_of_subsidiary = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if a trustee was also a director of a trading subsidiary for the financial period detailed. (True, False or NULL)",
    )
    does_trustee_receive_any_benefit = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if any of the trustees received any remuneration, payments or benefits from the charity other than refunds of legitimate trustee expenses for the financial period detailed. (True, False or NULL)",
    )
    trustee_payments_acting_as_trustee = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if any trustees received payments for acting as a trustee for the financial period detailed. (True, False or NULL)",
    )
    trustee_receives_payments_services = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if any trustees received payments for providing services to the charity for the financial period detailed. (True, False or NULL)",
    )
    trustee_receives_other_benefit = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if any trustees received any other benefit from the charity for the financial period detailed. (True, False or NULL)",
    )
    trustee_resigned_employment = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if any of the trustees resigned and took up employment with the charity during the financial period detailed. (True, False or NULL)",
    )
    employees_salary_over_60k = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if any of the charity's staff received total employee benefits of £60,000 or more. (True, False or NULL)",
    )
    count_salary_band_60001_70000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_70001_80000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_80001_90000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_90001_100000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_100001_110000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_110001_120000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_120001_130000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_130001_140000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_140001_150000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_150001_200000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_200001_250000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_250001_300000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_300001_350000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_350001_400000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_400001_450000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_450001_500000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_salary_band_over_500000 = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of staff whose total employment benefits were in this band for the financial period detailed.",
    )
    count_volunteers = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of Volunteers. The trustees' estimate of the number of people who undertook voluntary work in the UK for the charity during the year. The number shown is a head count and not expressed as full-time equivalents. Charities are invited to provide an estimate of volunteer numbers in their Annual Return but are not obliged to do so. Where a number is provided by the charity, including zero, that number is displayed.",
    )

    class Meta:
        verbose_name = "Annual Return - Part A"
        verbose_name_plural = "Annual Return - Part A"

    @property
    def count_salary_band_over_60000(self):
        return (
            (self.count_salary_band_60001_70000 or 0)
            + (self.count_salary_band_70001_80000 or 0)
            + (self.count_salary_band_80001_90000 or 0)
            + (self.count_salary_band_90001_100000 or 0)
            + (self.count_salary_band_100001_110000 or 0)
            + (self.count_salary_band_110001_120000 or 0)
            + (self.count_salary_band_120001_130000 or 0)
            + (self.count_salary_band_130001_140000 or 0)
            + (self.count_salary_band_140001_150000 or 0)
            + (self.count_salary_band_150001_200000 or 0)
            + (self.count_salary_band_200001_250000 or 0)
            + (self.count_salary_band_250001_300000 or 0)
            + (self.count_salary_band_300001_350000 or 0)
            + (self.count_salary_band_350001_400000 or 0)
            + (self.count_salary_band_400001_450000 or 0)
            + (self.count_salary_band_450001_500000 or 0)
            + (self.count_salary_band_over_500000 or 0)
        )

    @property
    def list_salary_band_over_60000(self):
        band_list = (
            {
                "employees": self.count_salary_band_60001_70000,
                "band_start": 60_001,
                "band_end": 70_000,
            },
            {
                "employees": self.count_salary_band_70001_80000,
                "band_start": 70_001,
                "band_end": 80_000,
            },
            {
                "employees": self.count_salary_band_80001_90000,
                "band_start": 80_001,
                "band_end": 90_000,
            },
            {
                "employees": self.count_salary_band_90001_100000,
                "band_start": 90_001,
                "band_end": 100_000,
            },
            {
                "employees": self.count_salary_band_100001_110000,
                "band_start": 100_001,
                "band_end": 110_000,
            },
            {
                "employees": self.count_salary_band_110001_120000,
                "band_start": 110_001,
                "band_end": 120_000,
            },
            {
                "employees": self.count_salary_band_120001_130000,
                "band_start": 120_001,
                "band_end": 130_000,
            },
            {
                "employees": self.count_salary_band_130001_140000,
                "band_start": 130_001,
                "band_end": 140_000,
            },
            {
                "employees": self.count_salary_band_140001_150000,
                "band_start": 140_001,
                "band_end": 150_000,
            },
            {
                "employees": self.count_salary_band_150001_200000,
                "band_start": 150_001,
                "band_end": 200_000,
            },
            {
                "employees": self.count_salary_band_200001_250000,
                "band_start": 200_001,
                "band_end": 250_000,
            },
            {
                "employees": self.count_salary_band_250001_300000,
                "band_start": 250_001,
                "band_end": 300_000,
            },
            {
                "employees": self.count_salary_band_300001_350000,
                "band_start": 300_001,
                "band_end": 350_000,
            },
            {
                "employees": self.count_salary_band_350001_400000,
                "band_start": 350_001,
                "band_end": 400_000,
            },
            {
                "employees": self.count_salary_band_400001_450000,
                "band_start": 400_001,
                "band_end": 450_000,
            },
            {
                "employees": self.count_salary_band_450001_500000,
                "band_start": 450_001,
                "band_end": 500_000,
            },
            {
                "employees": self.count_salary_band_over_500000,
                "band_start": 500_000,
                "band_end": None,
            },
        )
        return [b for b in band_list if b["employees"]]

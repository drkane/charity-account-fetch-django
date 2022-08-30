from django.contrib.postgres.fields import ArrayField
from django.db import models


class Charity(models.Model):
    charity_number = models.CharField(
        max_length=255,
        db_index=True,
        unique=True,
        verbose_name="Charity Number",
    )
    charity_name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Charity Name",
    )
    registered_date = models.DateField(
        verbose_name="Registered Date",
    )
    ceased_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ceased Date",
    )
    reason_for_removal = models.CharField(
        max_length=255,
        verbose_name="Reason for Removal",
        null=True,
        blank=True,
    )
    known_as = models.CharField(
        max_length=255,
        verbose_name="Known As",
        null=True,
        blank=True,
    )
    charity_status = models.CharField(
        max_length=255,
        verbose_name="Charity Status",
    )
    notes = models.TextField(
        verbose_name="Notes",
        null=True,
        blank=True,
    )
    postcode = models.CharField(
        max_length=255,
        verbose_name="Postcode",
        null=True,
        blank=True,
    )
    constitutional_form = models.CharField(
        max_length=255,
        verbose_name="Constitutional Form",
        null=True,
        blank=True,
    )
    previous_constitutional_form_1 = models.CharField(
        max_length=255,
        verbose_name="Previous Constitutional Form 1",
        null=True,
        blank=True,
    )
    geographical_spread = models.CharField(
        max_length=255,
        verbose_name="Geographical Spread",
        null=True,
        blank=True,
    )
    main_operating_location = models.CharField(
        max_length=255,
        verbose_name="Main Operating Location",
        null=True,
        blank=True,
    )
    purposes = ArrayField(
        models.CharField(max_length=255),
        verbose_name="Purposes",
        null=True,
        blank=True,
    )
    beneficiaries = ArrayField(
        models.CharField(max_length=255),
        verbose_name="Beneficiaries",
        null=True,
        blank=True,
    )
    activities = ArrayField(
        models.CharField(max_length=255),
        verbose_name="Activities",
        null=True,
        blank=True,
    )
    objectives = models.TextField(
        verbose_name="Objectives",
        null=True,
        blank=True,
    )
    principal_office_trustees_address = models.CharField(
        max_length=255,
        verbose_name="Principal Office/Trustees Address",
        null=True,
        blank=True,
    )
    website = models.URLField(
        verbose_name="Website",
        null=True,
        blank=True,
    )
    most_recent_year_income = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Most recent year income",
    )
    most_recent_year_expenditure = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Most recent year expenditure",
    )
    mailing_cycle = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Mailing cycle",
    )
    year_end = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Year End",
    )
    date_annual_return_received = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date annual return received",
    )
    next_year_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Next year end date",
    )
    donations_and_legacies_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Donations and legacies income",
    )
    charitable_activities_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Charitable activities income",
    )
    other_trading_activities_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Other trading activities income",
    )
    investments_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Investments income",
    )
    other_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Other income",
    )
    raising_funds_spending = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Raising funds spending",
    )
    charitable_activities_spending = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Charitable activities spending",
    )
    other_spending = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Other spending",
    )
    parent_charity_name = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Parent charity name",
    )
    parent_charity_number = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Parent charity number",
    )
    parent_charity_country_of_registration = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Parent charity country of registration",
    )
    designated_religious_body = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Designated religious body",
    )
    regulatory_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Regulatory Type",
    )

    class Meta:
        verbose_name = "Charity"
        verbose_name_plural = "Charities"


class CharityFinancialYear(models.Model):
    charity_number = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Charity Number",
    )
    most_recent_year_income = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Most recent year income",
    )
    most_recent_year_expenditure = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Most recent year expenditure",
    )
    mailing_cycle = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Mailing cycle",
    )
    year_end = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Year End",
    )
    date_annual_return_received = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date annual return received",
    )
    next_year_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Next year end date",
    )
    donations_and_legacies_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Donations and legacies income",
    )
    charitable_activities_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Charitable activities income",
    )
    other_trading_activities_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Other trading activities income",
    )
    investments_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Investments income",
    )
    other_income = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Other income",
    )
    raising_funds_spending = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Raising funds spending",
    )
    charitable_activities_spending = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Charitable activities spending",
    )
    other_spending = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Other spending",
    )

    class Meta:
        verbose_name = "Charity Financial Year"
        verbose_name_plural = "Charity Financial Years"
        unique_together = (("charity_number", "year_end"),)

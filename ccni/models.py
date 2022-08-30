from django.contrib.postgres.fields import ArrayField
from django.db import models


class Charity(models.Model):
    reg_charity_number = models.IntegerField(
        verbose_name="Reg charity number",
        db_index=True,
        unique=True,
    )
    sub_charity_number = models.IntegerField(
        verbose_name="Sub charity number", default=0
    )
    charity_name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Charity name",
    )
    date_registered = models.DateField(
        verbose_name="Date registered",
    )
    status = models.CharField(
        max_length=255,
        verbose_name="Status",
    )
    date_for_financial_year_ending = models.DateField(
        verbose_name="Date for financial year ending",
    )
    total_income = models.BigIntegerField(
        verbose_name="Total income",
    )
    total_spending = models.BigIntegerField(
        verbose_name="Total spending",
    )
    charitable_spending = models.BigIntegerField(
        verbose_name="Charitable spending",
    )
    income_generation_and_governance = models.BigIntegerField(
        verbose_name="Income generation and governance",
    )
    retained_for_future_use = models.BigIntegerField(
        verbose_name="Retained for future use",
    )
    public_address = models.TextField(
        verbose_name="Public address",
        null=True,
        blank=True,
    )
    website = models.URLField(
        verbose_name="Website",
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name="Email",
        null=True,
        blank=True,
    )
    telephone = models.CharField(
        max_length=255,
        verbose_name="Telephone",
        null=True,
        blank=True,
    )
    company_number = models.CharField(
        max_length=255,
        verbose_name="Company number",
        null=True,
        blank=True,
    )
    what_the_charity_does = ArrayField(
        models.CharField(max_length=255),
        verbose_name="What the charity does",
    )
    who_the_charity_helps = ArrayField(
        models.CharField(max_length=255),
        verbose_name="Who the charity helps",
    )
    how_the_charity_works = ArrayField(
        models.CharField(max_length=255),
        verbose_name="How the charity works",
    )

    class Meta:
        verbose_name = "Charity"
        verbose_name_plural = "Charities"

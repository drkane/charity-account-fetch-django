from django.db import models

from .charity import Charity


class CharityOtherRegulators(models.Model):
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
        related_name="other_regulators",
    )
    registered_charity_number = models.IntegerField(
        db_index=True,
        help_text="The registration number of the registered organisation allocated by the Commission. Note that a main charity and all its linked charities will share the same registered_charity_number.",
    )
    regulator_order = models.IntegerField(
        null=True,
        blank=True,
        help_text="A field to aid the ordering of the regulators for the charity.",
    )
    regulator_name = models.CharField(
        max_length=255, null=True, blank=True, help_text="The name of the regulator."
    )
    regulator_web_url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The web URL for the regulator.",
    )

    class Meta:
        verbose_name = "Other regulator"
        verbose_name_plural = "Other regulators"

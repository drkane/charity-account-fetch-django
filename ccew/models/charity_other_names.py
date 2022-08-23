from django.db import models

from .charity import Charity


class CharityOtherNames(models.Model):
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
        related_name="other_names",
    )
    registered_charity_number = models.IntegerField(
        db_index=True,
        help_text="The registration number of the registered organisation allocated by the Commission. Note that a main charity and all its linked charities will share the same registered_charity_number.",
    )
    linked_charity_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="A number that uniquely identifies the subsidiary or group member associated with a registered charity. Used for user identification purposes where the subsidiary is known by the parent registration number and the subsidiary number. The main parent charity has a linked_charity_number of 0.",
    )
    charity_name_id = models.IntegerField(
        null=True, blank=True, help_text="An id for the other charity name"
    )
    charity_name_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The type of other charity name. This can be working name or previous name.",
    )
    charity_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="The Main Name of the Charity",
    )

    class Meta:
        verbose_name = "Other name"
        verbose_name_plural = "Other names"

from django.db import models

from .charity import Charity


class CharityAreaOfOperation(models.Model):
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
        related_name="area_of_operation",
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
    geographic_area_type = models.CharField(
        max_length=255, null=True, blank=True, help_text="The area type for this row"
    )
    geographic_area_description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="The area descriptor for this row",
    )
    parent_geographic_area_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The parent area type. For example, if the area type is a country this indicator will be continent",
    )
    parent_geographic_area_description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The descriptor for the parent area type",
    )
    welsh_ind = models.BooleanField(null=True, blank=True)  # Indicates Welsh areas

    class Meta:
        verbose_name = "Area of Operation"
        verbose_name_plural = "Areas of Operation"

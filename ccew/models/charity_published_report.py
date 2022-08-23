from django.db import models

from .charity import Charity


class CharityPublishedReport(models.Model):
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
        related_name="published_reports",
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
    report_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The type of report that has been published in relation to the charity.",
    )
    report_location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The web URL for the location on the charity commission .gov site where the published report can be located.",
    )
    date_published = models.DateField(
        null=True,
        blank=True,
        help_text="The date that the message on the public register of charities to the report was published.",
    )

    class Meta:
        verbose_name = "Published Report"
        verbose_name_plural = "Published Reports"

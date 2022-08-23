from django.db import models

from .charity import Charity


class CharityEventHistory(models.Model):
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
        related_name="event_history",
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
    charity_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The Main Name of the Charity",
    )
    charity_event_order = models.IntegerField(
        null=True,
        blank=True,
        help_text="The order of the event in the charity history. 1 is the earliest event.",
    )
    event_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The type of charity event that has occurred.",
    )
    date_of_event = models.DateField(
        null=True, blank=True, help_text="The date that the event occurred."
    )
    reason = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The reason that the event occurred. A registration event will not have a reason available.",
    )
    assoc_organisation_number = models.IntegerField(
        null=True,
        blank=True,
        help_text="The charity id for the charity associated with the charity event. For example, in the case of asset transfer in this is the charity that has transferred the funds into the charity.",
    )
    assoc_registered_charity_number = models.IntegerField(
        db_index=True,
        null=True,
        blank=True,
        help_text="The registered charity number for the charity associated with the charity event. For example, in the case of asset transfer in this is the charity that has transferred the funds into the charity.",
    )
    assoc_charity_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The charity name of the charity associated with the charity event. For example, in the case of asset transfer in this is the charity that has transferred the funds into the charity.",
    )

    class Meta:
        verbose_name = "Event History"
        verbose_name_plural = "Event History"

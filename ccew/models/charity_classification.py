from django.db import models

from .charity import Charity


class CharityClassification(models.Model):
    class ClassificationType(models.TextChoices):
        WHAT = "What"
        HOW = "How"
        WHO = "Who"

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
        related_name="classification",
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
    classification_code = models.IntegerField(
        null=True,
        blank=True,
        help_text="The code of the classification described in the row",
    )
    classification_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        choices=ClassificationType.choices,
        help_text="The type of the classification. What - What the charity does. How - How the charity helps. Who - Who the charity helps",
    )
    classification_description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The descriptor of the classification code.",
    )

    class Meta:
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"

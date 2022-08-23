from django.db import models

from .charity import Charity


class CharityGoverningDocument(models.Model):
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
        related_name="governing_document",
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
    governing_document_description = models.TextField(
        null=True,
        blank=True,
        help_text="The description of the governing document. Note that this is not the governing document itself but the details of the original document and any subsequent amendments.",
    )
    charitable_objects = models.TextField(
        null=True, blank=True, help_text="The charitable objects of the charity."
    )
    area_of_benefit = models.TextField(
        null=True,
        blank=True,
        help_text="The area of benefit of the charity as defined in the governing document. This field can be blank as a charity does not have to define an area of benefit in the governing document.",
    )

    class Meta:
        verbose_name = "Governing Document"
        verbose_name_plural = "Governing Documents"

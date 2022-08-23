from django.db import models

from .charity import Charity


class CharityTrustee(models.Model):
    class IndividualOrOrganisation(models.TextChoices):
        INDIVIDUAL = "P"
        ORGANISATION = "O"

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
        related_name="trustees",
    )
    registered_charity_number = models.IntegerField(
        db_index=True,
        help_text="The registration number of the registered organisation allocated by the Commission. Note that a main charity and all its linked charities will share the same registered_charity_number.",
    )
    linked_charity_number = models.IntegerField(
        help_text="A number that uniquely identifies the subsidiary or group member associated with a registered charity. Used for user identification purposes where the subsidiary is known by the parent registration number and the subsidiary number. The main parent charity has a linked_charity_number of 0."
    )
    trustee_id = models.IntegerField(
        db_index=True, null=True, blank=True, help_text="The id number of the trustee."
    )
    trustee_name = models.CharField(
        max_length=255, null=True, blank=True, help_text="The name of the trustee."
    )
    trustee_is_chair = models.BooleanField(
        null=True,
        blank=True,
        help_text="TRUE if the trustee is the Chair. FALSE otherwise.",
    )
    individual_or_organisation = models.CharField(
        max_length=1,
        choices=IndividualOrOrganisation.choices,
        null=True,
        blank=True,
        help_text="A flag to denote whether the trustee is an individual or an organisation. O for organisation or P for an individual.",
    )
    trustee_date_of_appointment = models.DateField(
        null=True,
        blank=True,
        help_text="The date of appointment of the trustee for that charity.",
    )

    @property
    def other_trusteeships(self):
        return (
            CharityTrustee.objects.filter(trustee_id=self.trustee_id)
            .exclude(charity=self.charity)
            .all()
        )

    @property
    def sort_name(self):
        if (
            self.individual_or_organisation
            == self.IndividualOrOrganisation.ORGANISATION
        ):
            return self.trustee_name
        name = self.trustee_name.split()[::-1]
        for i, word in enumerate(name):
            if word.upper() in [
                "QC",
                "CBE",
                "MBE",
                "HONS",
                "PHD",
                "FCA",
                "BSC",
                "DL",
                "MR",
                "JP",
                "MRS",
            ]:
                continue
            return " ".join(name[i:])
        return " ".join(name)

    def __str__(self):
        return self.trustee_name

    class Meta:
        verbose_name = "Trustee"
        verbose_name_plural = "Trustees"

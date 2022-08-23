from django.db import models

from ccew.utils import to_titlecase


class Charity(models.Model):
    date_of_extract = models.DateField(
        null=True,
        blank=True,
        help_text="The date that the extract was taken from the main dataset.",
    )
    organisation_number = models.IntegerField(
        db_index=True,
        unique=True,
        help_text="The organisation number for the charity. This is the index value for the charity.",
    )
    registered_charity_number = models.IntegerField(
        db_index=True,
        help_text="The registration number of the registered organisation allocated by the Commission. Note that a main charity and all its linked charities will share the same registered_charity_number.",
    )
    linked_charity_number = models.IntegerField(
        db_index=True,
        help_text="A number that uniquely identifies the subsidiary or group member associated with a registered charity. Used for user identification purposes where the subsidiary is known by the parent registration number and the subsidiary number. The main parent charity has a linked_charity_number of 0.",
    )
    charity_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="The Main Name of the Charity",
    )
    charity_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="The type of the charity displayed on the public register of charities. Only the main parent charity will have a value for this field (i.e. linked_charity_number=0).",
    )
    charity_registration_status = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="The charity registration status indicates whether a charity is registered or removed",
    )
    date_of_registration = models.DateField(
        null=True,
        blank=True,
        help_text="The date the charity was registered with the Charity Commission.",
    )
    date_of_removal = models.DateField(
        null=True,
        blank=True,
        help_text="This is the date the charity was removed from the Register of Charities. This will not necessarily be the same date that the charity ceased to exist or ceased to operate. For non-removed charities the field is NULL.",
    )
    charity_reporting_status = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="The current reporting status of the charity",
    )
    latest_acc_fin_period_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="The start date of the latest financial period for which the charity has made a submission.",
    )
    latest_acc_fin_period_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="The end date of the latest financial period for which the charity has made a submission.",
    )
    latest_income = models.FloatField(
        null=True,
        blank=True,
        db_index=True,
        help_text="The latest income submitted by the charity. This is the total gross income submitted on part A of the annual return submission.",
    )
    latest_expenditure = models.FloatField(
        null=True,
        blank=True,
        help_text="The latest expenditure submitted by a charity. This is the expenditure submitted on part A of the annual return submission.",
    )
    charity_contact_address1 = models.CharField(
        max_length=255, null=True, blank=True, help_text="Charity Address Line 1"
    )
    charity_contact_address2 = models.CharField(
        max_length=255, null=True, blank=True, help_text="Charity Address Line 2"
    )
    charity_contact_address3 = models.CharField(
        max_length=255, null=True, blank=True, help_text="Charity Address Line 3"
    )
    charity_contact_address4 = models.CharField(
        max_length=255, null=True, blank=True, help_text="Charity Address Line 4"
    )
    charity_contact_address5 = models.CharField(
        max_length=255, null=True, blank=True, help_text="Charity Address Line 5"
    )
    charity_contact_postcode = models.CharField(
        max_length=255, null=True, blank=True, help_text="Charity Postcode"
    )
    charity_contact_phone = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Charity Public Telephone Number",
    )
    charity_contact_email = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Charity Public email address",
    )
    charity_contact_web = models.CharField(
        max_length=255, null=True, blank=True, help_text="Charity Website Address"
    )
    charity_company_registration_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Registered Company Number of the Charity as assigned by Companies House. Integer returned as string",
    )
    charity_insolvent = models.BooleanField(
        null=True, blank=True, help_text="Indicates if the charity is insolvent."
    )
    charity_in_administration = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates if the charity is in administration.",
    )
    charity_previously_excepted = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates the charity was previously an excepted charity.",
    )
    charity_is_cdf_or_cif = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Indicates whether the charity is a Common Investment Fund or Common Deposit Fund.",
    )
    charity_is_cio = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates whether the charity is a Charitable Incorporated Organisation.",
    )
    cio_is_dissolved = models.BooleanField(
        null=True, blank=True, help_text="Indicates the CIO is to be dissolved."
    )
    date_cio_dissolution_notice = models.DateField(
        null=True, blank=True, help_text="Date the CIO dissolution notice expires"
    )
    charity_activities = models.TextField(
        null=True,
        blank=True,
        help_text="The charity activities, the trustees’ description of what they do and who they help.",
    )
    charity_gift_aid = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates whether the charity is registered for gift aid with HMRC. True, False, NULL (not known)",
    )
    charity_has_land = models.BooleanField(
        null=True,
        blank=True,
        help_text="Indicates whether the charity owns or leases any land or buildings. True, False, NULL (not known)",
    )

    def __str__(self):
        """Return a string representation of the model"""
        return "{} [{}{}]".format(
            to_titlecase(self.charity_name),
            self.registered_charity_number,
            "-{}".format(self.linked_charity_number)
            if self.linked_charity_number
            else "",
        )

    @property
    def name(self):
        return to_titlecase(self.charity_name)

    @property
    def org_id(self):
        return "GB-CHC-{}".format(self.registered_charity_number)

    @property
    def ccew_url(self):
        return "https://register-of-charities.charitycommission.gov.uk/charity-search/-/charity-details/{}".format(
            self.registered_charity_number
        )

    @property
    def aoo(self):
        result = {
            "uk": [],
            "overseas": [],
        }
        for area in self.area_of_operation.all():
            if area.geographic_area_type in ("Country", "Continent"):
                if area.geographic_area_description in ("Scotland", "Northern Ireland"):
                    result["uk"].append(area)
                else:
                    result["overseas"].append(area)
            else:
                result["uk"].append(area)
        return result

    @property
    def latest_financials(self):
        return self.financials()

    def address(self, join=None):
        address_fields = [
            self.charity_contact_address1,
            self.charity_contact_address2,
            self.charity_contact_address3,
            self.charity_contact_address4,
            self.charity_contact_address5,
            self.charity_contact_postcode,
        ]
        address_fields = [a for a in address_fields if a]
        if isinstance(join, str):
            return join.join(address_fields)
        return address_fields

    def financials(self, on_date=None):
        if on_date:
            finances_parta = self.annual_return_part_a.filter(
                fin_period_end_date__gte=on_date,
                fin_period_start_date__lte=on_date,
            ).first()
        else:
            finances_parta = self.annual_return_part_a.filter(
                latest_fin_period_submitted_ind=True
            ).first()
        finances_partb = (
            self.annual_return_part_b.filter(
                fin_period_end_date=finances_parta.fin_period_end_date
            ).first()
            if finances_parta
            else None
        )
        return {
            "parta": finances_parta,
            "partb": finances_partb,
        }

    class Meta:
        verbose_name = "Charity"
        verbose_name_plural = "Charities"

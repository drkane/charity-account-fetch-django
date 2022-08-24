from django.db import models
from django.utils.translation import gettext_lazy as _

from ccew.utils import to_titlecase
from documents.utils import convert_file


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Tag name"))

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    def __str__(self):
        return self.name


class Regulators(models.TextChoices):
    CCEW = "CCEW", _("Charity Commission for England and Wales")
    OSCR = "OSCR", _("Office of the Scottish Charity Regulator")
    CCNI = "CCNI", _("Charity Commission for Northern Ireland")


class Charity(models.Model):

    org_id = models.CharField(max_length=50, primary_key=True)
    source = models.CharField(max_length=4, choices=Regulators.choices, null=True)
    name = models.CharField(max_length=255, null=True, db_index=True)
    date_registered = models.DateField(null=True)
    date_removed = models.DateField(null=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="charities")

    @property
    def is_active(self):
        return self.date_removed is None

    class Meta:
        verbose_name = _("charity")
        verbose_name_plural = _("charities")

    def __str__(self):
        return "{} [{}]".format(
            to_titlecase(self.name),
            self.org_id,
        )


class CharityFinancialYear(models.Model):
    charity = models.ForeignKey(
        Charity, on_delete=models.CASCADE, related_name="financial_years"
    )
    financial_year_end = models.DateField(db_index=True)
    document_due = models.DateField()
    document_submitted = models.DateField(blank=True, null=True)
    income = models.BigIntegerField(blank=True, null=True)
    expenditure = models.BigIntegerField(blank=True, null=True)

    task_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Task ID if the document is currently being fetched",
    )

    class Meta:
        unique_together = (
            "charity",
            "financial_year_end",
        )

    def __str__(self):
        return "{} [{}]".format(
            to_titlecase(self.charity.name),
            self.financial_year_end,
        )


class Document(models.Model):
    class DocumentTypes(models.TextChoices):
        PDF = "application/pdf", _("PDF")

    class DocumentLanguages(models.TextChoices):
        EN = "en", _("English")

    financial_year = models.ForeignKey(
        CharityFinancialYear, on_delete=models.CASCADE, related_name="documents"
    )
    content = models.TextField(blank=True, null=True)
    content_length = models.IntegerField(blank=True, null=True)
    content_type = models.CharField(
        max_length=50, choices=DocumentTypes.choices, default=DocumentTypes.PDF
    )
    language = models.CharField(
        max_length=2, choices=DocumentLanguages.choices, default=DocumentLanguages.EN
    )
    pages = models.IntegerField(blank=True, null=True)
    file = models.FileField(upload_to="data/documents", blank=True, null=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="documents")

    def save(self, *args, **kwargs):
        if not self.content:
            filedata = convert_file(self.file)
            self.content = filedata["content"]
            self.content_length = filedata["content_length"]
            self.pages = filedata["pages"]
            self.content_type = filedata["content_type"]
            self.language = filedata["language"]
        if not self.content_length:
            self.content_length = len(self.content)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.financial_year.__str__()

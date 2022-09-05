import io
import logging
import uuid

import ocrmypdf
from autoslug import AutoSlugField
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_q.tasks import (
    Iter,
    Task,
    async_task,
    count_group,
    fetch_group,
    result_group,
)

from ccew.utils import to_titlecase
from documents.utils import convert_file


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Tag name"))
    slug = AutoSlugField(populate_from="name", unique=True)

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")

    def __str__(self):
        return self.name


class Regulators(models.TextChoices):
    CCEW = "CCEW", _("Charity Commission for England and Wales")
    OSCR = "OSCR", _("Office of the Scottish Charity Regulator")
    CCNI = "CCNI", _("Charity Commission for Northern Ireland")
    MAN = "MAN", _("Manually added charity")


class DocumentStatus(models.TextChoices):
    SUCCESS = "SUCCESS", _("Document successfully fetched")
    FAILED = "FAILED", _("Document fetching failed")
    PENDING = "PENDING", _("Document not yet fetched")


class Charity(models.Model):

    org_id = models.CharField(max_length=50, primary_key=True)
    source = models.CharField(
        max_length=4, choices=Regulators.choices, default=Regulators.MAN
    )
    name = models.CharField(max_length=255, null=True, db_index=True)
    date_registered = models.DateField(null=True)
    date_removed = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


class FetchGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

    def update_task_group(self):
        self.failure_count = count_group(self.id, failures=True)
        self.success_count = count_group(self.id) - self.failure_count
        self.updated_at = timezone.now()
        for fy in self.financial_years.all():
            fy.save()
        self.save()

    @property
    def pending_count(self):
        return self.task_count - self.success_count - self.failure_count

    def tasks(self, limit=None):
        fy_seen = set()
        count = 0
        for fy in self.financial_years.all():
            if fy.task_id:
                fy_seen.add(fy.task_id)
                count += 1
                if limit and count > limit:
                    break
                yield Task.get_task(fy.task_id), fy
            else:
                count += 1
                if limit and count > limit:
                    break
                yield None, fy
        if fetch_group(self.id):
            for task in fetch_group(self.id).exclude(id__in=fy_seen):
                if task.func == "documents.fetch.fetch_documents_for_charity":
                    try:
                        fy = CharityFinancialYear.objects.get(task_id=task.id)
                        count += 1
                        if limit and count > limit:
                            break
                        yield task, fy
                        continue
                    except CharityFinancialYear.DoesNotExist:
                        pass
                count += 1
                if limit and count > limit:
                    break
                yield task, None

    class Meta:
        verbose_name = _("fetch group")
        verbose_name_plural = _("fetch groups")


class CharityFinancialYear(models.Model):
    charity = models.ForeignKey(
        Charity, on_delete=models.CASCADE, related_name="financial_years"
    )
    financial_year_end = models.DateField(db_index=True)
    document_due = models.DateField(blank=True, null=True)
    document_submitted = models.DateField(blank=True, null=True)
    income = models.BigIntegerField(blank=True, null=True)
    expenditure = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=15,
        choices=DocumentStatus.choices,
        blank=True,
        null=True,
        default=None,
    )
    task_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Task ID if the document is currently being fetched",
    )
    task_groups = models.ManyToManyField(FetchGroup, related_name="financial_years")
    status_notes = models.TextField(blank=True, null=True)

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

    def save(self, *args, **kwargs):

        if self.task_id:
            task = Task.get_task(self.task_id)
            if not task:
                self.status = DocumentStatus.PENDING
            elif task.success and task.result:
                self.status = DocumentStatus.SUCCESS
            else:
                self.status = DocumentStatus.FAILED
                self.status_notes = task.result

        document = self.documents.first()
        if document and document.content_length:
            if document.content_length > settings.MIN_DOC_LENGTH:
                self.status = DocumentStatus.SUCCESS
            elif document.content_length > 0:
                self.status = DocumentStatus.FAILED
                self.status_notes = "Document too short"
        if document and not document.content:
            self.status = DocumentStatus.FAILED
            self.status_notes = "No document found"
        super().save(*args, **kwargs)


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
        max_length=50,
        choices=DocumentTypes.choices,
        default=None,
        blank=True,
        null=True,
    )
    language = models.CharField(
        max_length=2,
        choices=DocumentLanguages.choices,
        default=None,
        blank=True,
        null=True,
    )
    pages = models.IntegerField(blank=True, null=True)
    file = models.FileField(upload_to="data/documents", blank=True, null=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="documents")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def convert_file(self, file_obj, *args, **kwargs):
        filedata = convert_file(file_obj)
        self.file = file_obj
        self.content = filedata["content"]
        self.content_length = filedata["content_length"]
        self.pages = filedata["pages"]
        self.content_type = filedata["content_type"]
        self.language = filedata["language"]
        logging.debug(
            "PDF file fetched pages: {:,.0f} size: {:,.0f}".format(
                self.pages, self.content_length
            )
        )

    def do_document_ocr(self, *args, **kwargs):
        try:
            buffer = io.BytesIO()
            ocrmypdf.ocr(self.file, buffer, **settings.OCRMYPDF_OPTIONS)
            logging.info("OCRing PDF")
            pdf_file = ContentFile(
                buffer.getvalue(),
                name=f"{self.financial_year.org_id}-{self.financial_year.financial_year_end}.pdf",
            )
            self.convert_file(pdf_file)
        except ocrmypdf.exceptions.PriorOcrFoundError:
            logging.info("PDF already OCR'd")
        except ocrmypdf.exceptions.EncryptedPdfError:
            logging.info("PDF is encrypted")

    def save(self, *args, **kwargs):
        if not self.content and self.file:
            self.convert_file(self.file)

            # OCR the PDF if necessary
            if self.content_length < settings.MIN_DOC_LENGTH:
                self.do_document_ocr()

        if not self.content_length and self.content:
            self.content_length = len(self.content)

        # save the financial year (resets the status)
        self.financial_year.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.financial_year.__str__()

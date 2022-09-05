from django.conf import settings
from django.db import migrations, models, transaction

from documents.models import DocumentStatus


def migrate_data_forward(apps, schema_editor):
    CharityFinancialYear = apps.get_model("documents", "CharityFinancialYear")
    with transaction.atomic():
        for instance in CharityFinancialYear.objects.filter(documents__isnull=False):
            document = instance.documents.first()
            if document.content_length > settings.MIN_DOC_LENGTH:
                instance.status = DocumentStatus.SUCCESS
                instance.task_id = None
            elif document.content_length > 0:
                instance.status = DocumentStatus.FAILED
                instance.status_notes = "Document too short"
                instance.task_id = None
            instance.save()


def migrate_data_backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0009_tag_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="charityfinancialyear",
            name="status",
            field=models.CharField(
                choices=[
                    ("SUCCESS", "Document successfully fetched"),
                    ("FAILED", "Document fetching failed"),
                    ("PENDING", "Document not yet fetched"),
                ],
                blank=True,
                null=True,
                default=None,
                max_length=15,
            ),
        ),
        migrations.AddField(
            model_name="charityfinancialyear",
            name="status_notes",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
        migrations.AlterField(
            model_name="document",
            name="content_type",
            field=models.CharField(
                blank=True,
                choices=[("application/pdf", "PDF")],
                default=None,
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="language",
            field=models.CharField(
                blank=True,
                choices=[("en", "English")],
                default=None,
                max_length=2,
                null=True,
            ),
        ),
    ]

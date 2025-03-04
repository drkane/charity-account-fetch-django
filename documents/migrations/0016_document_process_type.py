# Generated by Django 4.1 on 2024-07-25 10:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0015_charityfinancialyear_last_document_fetch_started"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="process_type",
            field=models.CharField(
                blank=True,
                choices=[("AS", "As supplied"), ("OCR", "OCR")],
                default=None,
                max_length=3,
                null=True,
            ),
        ),
    ]

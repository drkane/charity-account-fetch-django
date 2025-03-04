# Generated by Django 4.1 on 2022-08-23 17:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Charity",
            fields=[
                (
                    "org_id",
                    models.CharField(max_length=50, primary_key=True, serialize=False),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("CCEW", "Charity Commission for England and Wales"),
                            ("OSCR", "Office of the Scottish Charity Regulator"),
                            ("CCNI", "Charity Commission for Northern Ireland"),
                        ],
                        max_length=4,
                        null=True,
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=255, null=True)),
                ("date_registered", models.DateField(null=True)),
                ("date_removed", models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CharityFinancialYear",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("financial_year_end", models.DateField(db_index=True)),
                ("document_due", models.DateField()),
                ("document_submitted", models.DateField(blank=True, null=True)),
                ("income", models.BigIntegerField(blank=True, null=True)),
                ("expenditure", models.BigIntegerField(blank=True, null=True)),
                (
                    "charity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="documents.charity",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="Tag name")),
            ],
            options={
                "verbose_name": "tag",
                "verbose_name_plural": "tags",
            },
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(blank=True, null=True)),
                ("content_length", models.IntegerField(blank=True, null=True)),
                ("pages", models.IntegerField(blank=True, null=True)),
                (
                    "file",
                    models.FileField(blank=True, null=True, upload_to="documents"),
                ),
                (
                    "financial_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="documents.charityfinancialyear",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="charity",
            name="tags",
            field=models.ManyToManyField(blank=True, to="documents.tag"),
        ),
    ]

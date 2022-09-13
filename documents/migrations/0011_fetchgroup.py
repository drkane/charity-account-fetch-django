# Generated by Django 4.1 on 2022-09-05 18:07

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "documents",
            "0010_remove_charityfinancialyear_task_id_document_status_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="FetchGroup",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("task_count", models.IntegerField(default=0)),
                ("failure_count", models.IntegerField(default=0)),
                ("success_count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "fetch group",
                "verbose_name_plural": "fetch groups",
            },
        ),
    ]
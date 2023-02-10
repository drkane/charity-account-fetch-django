# Generated by Django 4.1 on 2023-02-10 13:19

from django.db import migrations, models
from tqdm import tqdm


def update_last_fetch_started(apps, schema_editor):
    CharityFinancialYear = apps.get_model("documents", "CharityFinancialYear")
    Task = apps.get_model("django_q", "Task")
    for fy in tqdm(
        CharityFinancialYear.objects.prefetch_related("documents")
        .filter(last_document_fetch_started__isnull=True)
        .filter(models.Q(task_id__isnull=False) | models.Q(documents__isnull=False))
    ):
        if fy.documents.count():
            fy.last_document_fetch_started = fy.documents.first().created_at
            fy.save()
        elif fy.task_id:
            task = Task.objects.get(id=fy.task_id)
            if task and task.started:
                fy.last_document_fetch_started = task.started
                fy.save()


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0014_alter_charity_date_registered_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="charityfinancialyear",
            name="last_document_fetch_started",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(update_last_fetch_started, migrations.RunPython.noop),
    ]

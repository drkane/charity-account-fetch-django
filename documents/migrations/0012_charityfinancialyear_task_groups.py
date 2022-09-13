# Generated by Django 4.1 on 2022-09-05 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0011_fetchgroup"),
    ]

    operations = [
        migrations.AddField(
            model_name="charityfinancialyear",
            name="task_groups",
            field=models.ManyToManyField(
                related_name="financial_years", to="documents.fetchgroup"
            ),
        ),
    ]
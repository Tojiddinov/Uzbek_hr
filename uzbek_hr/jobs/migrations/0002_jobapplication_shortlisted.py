# Generated by Django 5.1.5 on 2025-02-26 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobapplication",
            name="shortlisted",
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 5.1.6 on 2025-03-18 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="response",
            name="respondent_email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="response",
            name="respondent_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

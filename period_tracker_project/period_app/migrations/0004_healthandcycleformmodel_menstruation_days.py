# Generated by Django 5.1.5 on 2025-01-22 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('period_app', '0003_healthandcycleformmodel_pregnancy_end_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='healthandcycleformmodel',
            name='menstruation_days',
            field=models.JSONField(default=list),
        ),
    ]
# Generated by Django 5.1.5 on 2025-01-25 13:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('period_app', '0005_alter_healthandcycleformmodel_daily_mood_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statisticscycleinfo',
            name='user_profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cycle_info', to='period_app.userprofile'),
        ),
    ]

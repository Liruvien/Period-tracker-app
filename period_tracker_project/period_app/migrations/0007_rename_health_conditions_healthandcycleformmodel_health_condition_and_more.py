# Generated by Django 5.1.5 on 2025-01-26 22:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('period_app', '0006_alter_statisticscycleinfo_user_profile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='healthandcycleformmodel',
            old_name='health_conditions',
            new_name='health_condition',
        ),
        migrations.RenameField(
            model_name='statisticscycleinfo',
            old_name='health_conditions',
            new_name='health_condition',
        ),
    ]
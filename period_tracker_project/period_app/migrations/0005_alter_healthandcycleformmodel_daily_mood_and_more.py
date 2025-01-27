# Generated by Django 5.1.5 on 2025-01-25 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('period_app', '0004_remove_statisticscycleinfo_mood_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthandcycleformmodel',
            name='daily_mood',
            field=models.CharField(blank=True, choices=[('1', 'Szczęście'), ('2', 'Entuzjazm'), ('3', 'Ekscytacja'), ('4', 'Smutek'), ('5', 'Rozpacz'), ('6', 'Lęk'), ('7', 'Irytacja'), ('8', 'Gniew'), ('9', 'Radość'), ('10', 'Placz'), ('11', 'Strach'), ('12', 'Złość'), ('13', 'Wstręt'), ('14', 'Rozpacz'), ('15', 'Panika')], max_length=255),
        ),
        migrations.AlterField(
            model_name='statisticscycleinfo',
            name='daily_mood',
            field=models.CharField(blank=True, choices=[('1', 'Szczęście'), ('2', 'Entuzjazm'), ('3', 'Ekscytacja'), ('4', 'Smutek'), ('5', 'Rozpacz'), ('6', 'Lęk'), ('7', 'Irytacja'), ('8', 'Gniew'), ('9', 'Radość'), ('10', 'Placz'), ('11', 'Strach'), ('12', 'Złość'), ('13', 'Wstręt'), ('14', 'Rozpacz'), ('15', 'Panika')], max_length=255),
        ),
    ]

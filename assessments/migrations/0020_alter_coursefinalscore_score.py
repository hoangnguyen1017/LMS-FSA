# Generated by Django 5.0.1 on 2024-11-14 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0019_coursefinalscore_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursefinalscore',
            name='score',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]

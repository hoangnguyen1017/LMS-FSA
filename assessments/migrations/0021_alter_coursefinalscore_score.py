# Generated by Django 5.0.1 on 2024-11-14 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0020_alter_coursefinalscore_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursefinalscore',
            name='score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

# Generated by Django 5.1.1 on 2024-10-23 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assignment_name', models.CharField(max_length=100, verbose_name='Assignment Name')),
                ('content', models.TextField(blank=True, null=True, verbose_name='Assignment Content')),
                ('score', models.IntegerField(default=0, verbose_name='Score')),
                ('note', models.TextField(blank=True, verbose_name='Notes')),
                ('start_date', models.DateTimeField(verbose_name='Start Date')),
                ('end_date', models.DateTimeField(verbose_name='End Date')),
            ],
            options={
                'verbose_name': 'Assignment',
                'verbose_name_plural': 'Assignments',
                'ordering': ['start_date'],
            },
        ),
    ]

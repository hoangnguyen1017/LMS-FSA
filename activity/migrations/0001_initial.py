# Generated by Django 5.1.1 on 2024-10-25 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserActivityLog',
            fields=[
                ('log_id', models.AutoField(primary_key=True, serialize=False)),
                ('activity_type', models.CharField(choices=[('login', 'Login'), ('course_completion', 'Course Completion'), ('logout', 'Logout'), ('page_visit', 'Page Visit')], max_length=100)),
                ('activity_details', models.TextField(blank=True, null=True)),
                ('activity_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

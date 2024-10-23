# Generated by Django 5.1.1 on 2024-10-23 12:44

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('invited_count', models.IntegerField(default=0, verbose_name='Invited Count')),
                ('assessed_count', models.IntegerField(default=0, verbose_name='Assessed Count')),
                ('qualified_count', models.IntegerField(default=0, verbose_name='Qualified Count')),
                ('qualify_score', models.IntegerField(default=60, verbose_name='Qualify Score')),
                ('total_score', models.IntegerField(default=100, verbose_name='Total Score')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('time_limit', models.IntegerField(default=0)),
                ('invited_emails', models.TextField(blank=True, verbose_name='Invited Candidates')),
            ],
            options={
                'verbose_name': 'Assessment',
                'verbose_name_plural': 'Assessments',
                'ordering': ['created_at', 'course'],
            },
        ),
        migrations.CreateModel(
            name='AssessmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Assessment Type',
                'verbose_name_plural': 'Assessment Types',
            },
        ),
        migrations.CreateModel(
            name='InvitedCandidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('invitation_date', models.DateTimeField(auto_now_add=True)),
                ('expiration_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NonRegisteredCandidateAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('score_quiz', models.IntegerField(default=0, verbose_name='Quiz Score')),
                ('score_ass', models.IntegerField(default=0, verbose_name='Assignment Score')),
                ('note', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('attempt_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Non-Registered Candidate Attempt',
                'verbose_name_plural': 'Non-Registered Candidate Attempts',
            },
        ),
        migrations.CreateModel(
            name='StudentAssessmentAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score_quiz', models.IntegerField(default=0, verbose_name='Quiz Score')),
                ('score_ass', models.IntegerField(default=0, verbose_name='Assignment Score')),
                ('note', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('attempt_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Student Assignment Attempt',
                'verbose_name_plural': 'Student Assignment Attempts',
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_response', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('score', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]

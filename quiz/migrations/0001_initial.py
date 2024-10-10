# Generated by Django 5.0.9 on 2024-10-10 06:10

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("category", "0001_initial"),
        ("course", "0001_initial"),
        ("question", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Quiz",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("due_date", models.DateTimeField(blank=True, null=True)),
                (
                    "attempts_allowed",
                    models.PositiveIntegerField(
                        default=1,
                        help_text="Number of times a student can take this quiz",
                    ),
                ),
                (
                    "grading_method",
                    models.CharField(
                        choices=[
                            ("HIGHEST", "Highest Score"),
                            ("AVERAGE", "Average Score"),
                            ("LATEST", "Latest Score"),
                        ],
                        default="HIGHEST",
                        max_length=10,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="category.category",
                    ),
                ),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="course.course"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_quizzes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("questions", models.ManyToManyField(to="question.question")),
            ],
        ),
        migrations.CreateModel(
            name="Submission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("grade", models.FloatField(blank=True, null=True)),
                (
                    "submitted_file",
                    models.FileField(
                        blank=True, null=True, upload_to="quiz_submissions/"
                    ),
                ),
                ("due_date", models.DateTimeField(blank=True, null=True)),
                (
                    "quiz",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="quiz.quiz"
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quiz_submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SubmittedAnswer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(default="", max_length=255)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="question.question",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submitted_answers",
                        to="quiz.submission",
                    ),
                ),
            ],
        ),
    ]

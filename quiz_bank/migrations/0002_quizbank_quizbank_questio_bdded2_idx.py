# Generated by Django 5.0.9 on 2024-11-02 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_initial'),
        ('quiz_bank', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='quizbank',
            index=models.Index(fields=['question_type'], name='QuizBank_questio_bdded2_idx'),
        ),
    ]

# Create your models here.
from django.db import models
from django.utils import timezone
from django.conf import settings
from quiz.models import Quiz, Question
from coding_exercise.models import Exercise

class Assessment(models.Model):
    title = models.CharField(max_length=255)
    quizzes = models.ManyToManyField(Quiz, related_name='assessments', blank=True)
    exercises = models.ManyToManyField(Exercise, related_name='assessments', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assessments')

    def __str__(self):
        return self.title

    def is_past_due(self):
        if self.due_date:
            return timezone.now() > self.due_date
        return False
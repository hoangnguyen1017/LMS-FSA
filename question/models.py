from django.db import models
from category.models import Category, SubCategory  # Add SubCategory import
from subject.models import Subject
from django.utils import timezone

class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)  # Add this line
    correct_answer = models.CharField(max_length=255, default='')  # Added with default value
    question_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)  # Changed from 'answer_text' to 'text'
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

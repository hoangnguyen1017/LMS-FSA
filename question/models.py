from django.db import models
from category.models import Category
from subject.models import Subject

class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=254)

    def __str__(self):
        return self.question_text
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=254)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

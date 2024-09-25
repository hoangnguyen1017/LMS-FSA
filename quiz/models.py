from django.db import models

from subject.models import Subject



class QuizQuestionAnswer(models.Model):
    question_description = models.TextField(max_length=255)
    answertext_1 = models.TextField(max_length=255)
    answertext_2 = models.TextField(max_length=255)
    answertext_3 = models.TextField(max_length=255)
    answertext_4 = models.TextField(max_length=255)
    correct_answer = models.CharField(max_length=255, choices=[('answertext_1', 'Answer 1'), ('answertext_2', 'Answer 2'), ('answertext_3', 'Answer 3'), ('answertext_4', 'Answer 4')])

    def __str__(self):
        return self.question_description

class UserAnswer(models.Model):
    question = models.ForeignKey(QuizQuestionAnswer, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=255, choices=[
        ('answertext_1', 'Answer 1'),
        ('answertext_2', 'Answer 2'),
        ('answertext_3', 'Answer 3'),
        ('answertext_4', 'Answer 4')
    ], default='No answer')

    def __str__(self):
        return f'User answer for: {self.question}'
    


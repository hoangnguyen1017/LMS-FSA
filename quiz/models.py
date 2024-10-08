# models.py
from django.db import models
from course.models import Course

from django.contrib.auth.models import User  # Assuming User is the built-in Django User model

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    quiz_title = models.CharField(max_length=255)
    quiz_description = models.TextField(blank=True)
    total_marks = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_limit = models.IntegerField(default=0)

    start_datetime = models.DateTimeField(null=True, blank=True)  
    end_datetime = models.DateTimeField(null=True, blank=True)    
    attempts_allowed = models.PositiveIntegerField(default=1)  

    def __str__(self):
        return self.quiz_title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=50)  # E.g., multiple-choice, true/false
    points = models.IntegerField()

    def __str__(self):
        return self.question_text

class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text

# Model for Student Quiz Attempt
class StudentQuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    attempt_date = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(null=True, blank=True)
    is_proctored = models.BooleanField(default=False)
    proctoring_data = models.JSONField(null=True, blank=True)

# Model for Student Answer
class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentQuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.SET_NULL, null=True)

# Model for AI Grading
class AIGrading(models.Model):
    answer = models.ForeignKey(StudentAnswer, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    awarded_points = models.IntegerField()

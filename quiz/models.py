from django.db import models
from category.models import Category
from course.models import Course
from question.models import Question, Answer
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from module_group.models import Module  # Import the Module model instead of ModuleGroup
from django.core.files.base import ContentFile

User = get_user_model()


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    questions = models.ManyToManyField('question.Question')
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_quizzes')
    due_date = models.DateTimeField(null=True, blank=True)
    attempts_allowed = models.PositiveIntegerField(default=1, help_text="Number of times a student can take this quiz")
    GRADING_METHODS = [
        ('HIGHEST', 'Highest Score'),
        ('AVERAGE', 'Average Score'),
        ('LATEST', 'Latest Score'),
    ]
    grading_method = models.CharField(max_length=10, choices=GRADING_METHODS, default='HIGHEST')

    def __str__(self):
        return self.title

    def is_past_due(self):
        if self.due_date:
            if timezone.is_naive(self.due_date):
                self.due_date = timezone.make_aware(self.due_date)
            return timezone.now() > self.due_date
        return False

    def is_open_for_submission(self):
        if self.due_date:
            if timezone.is_naive(self.due_date):
                self.due_date = timezone.make_aware(self.due_date)
            return timezone.now() <= self.due_date
        return True  # If there's no due date, the quiz is always open

    def attempts_left(self, user):
        submissions = Submission.objects.filter(quiz=self, student=user).count()
        return max(0, self.attempts_allowed - submissions)

    def calculate_grade(self, user):
        submissions = self.submission_set.filter(student=user)
        if not submissions:
            return None

        grades = [sub.grade for sub in submissions if sub.grade is not None]
        if not grades:
            return None

        if self.grading_method == 'HIGHEST':
            return max(grades)
        elif self.grading_method == 'AVERAGE':
            return sum(grades) / len(grades)
        else:  # 'LATEST'
            return grades[-1]

class Submission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.FloatField(null=True, blank=True)
    submitted_file = models.FileField(upload_to='quiz_submissions/', null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)  # Uncomment this line

    def __str__(self):
        return f"{self.student.username}'s submission for {self.quiz.title}"

    def calculate_score(self):
        total_questions = self.quiz.questions.count()
        correct_answers = sum(1 for answer in self.submitted_answers.all() if answer.is_correct())
        return (correct_answers / total_questions) * 10 if total_questions > 0 else 0

    def save(self, *args, **kwargs):
        if self.quiz.is_past_due():
            raise ValueError("Cannot submit a quiz past its due date.")
        super().save(*args, **kwargs)

class SubmittedAnswer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='submitted_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, default='')  # Add default value here

    def __str__(self):
        return f"Answer for {self.question} in {self.submission}"

    def is_correct(self):
        correct_answer = self.question.answers.filter(is_correct=True).first()
        return correct_answer and self.text.lower().strip() == correct_answer.text.lower().strip()

from django.db import models
from django.utils import timezone
from django.conf import settings
from quiz.models import Quiz  # Adjust based on your project structure
from assignment.models import Assignment  # Adjust based on your project structure
from django.core.exceptions import ValidationError  # Import ValidationError
from course.models import Course

class Assessment(models.Model):
    # Set a unique related_name for the course field
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments', verbose_name="Course")

    title = models.CharField(max_length=255)
    
    # Foreign keys to Quiz and Assignment (both optional)
    quiz = models.ForeignKey(Quiz, related_name='assessments', null=True, blank=True, on_delete=models.SET_NULL)
    assignment = models.ForeignKey(Assignment, related_name='assessments', null=True, blank=True, on_delete=models.SET_NULL)

    total_score = models.IntegerField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assessments')

    def __str__(self):
        return self.title

    def is_past_due(self):
        """Check if the due date has passed."""
        if self.due_date:
            return timezone.now() > self.due_date
        return False

    def clean(self):
        """
        Ensure that either a `quiz`, an `assignment`, or both are set.
        """
        if not self.quiz and not self.assignment:
            raise ValidationError("An assessment must include at least a quiz or an assignment.")

    class Meta:
        ordering = ['due_date', 'created_at']

# Model for Student Assignment Attempt
class StudentAssessmentAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    # Scoring and feedback
    score_quiz = models.IntegerField(default=0, verbose_name="Score")
    score_ass = models.IntegerField(default=0, verbose_name="Score")

    note = models.TextField(blank=True, null=True, verbose_name="Notes")

    # Timestamps and User relations
    attempt_date = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        verbose_name = "Student Assignment Attempt"
        verbose_name_plural = "Student Assignment Attempts"

    def __str__(self):
        return f"Attempt by {self.user} for {self.assignment}"

    def clean(self):
        """Validation to ensure score is non-negative and within reasonable bounds."""
        if self.score < 0 or self.score > 100:  # Adjust range as per your scoring system
            raise ValidationError("Score must be between 0 and 100.")
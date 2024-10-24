from django.db import models
from exercises.models import Exercise
from course.models import Course
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

class Assignment(models.Model):
    # General assignment information
    assignment_name = models.CharField(max_length=100, verbose_name="Assignment Name")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments', verbose_name="Course")
    

    # Content of the assignment (normal assignment)
    content = models.TextField(blank=True, null=True, verbose_name="Assignment Content") 

    # Coding exercises (optional, can have multiple coding exercises)
    coding_exercises = models.ManyToManyField(Exercise, blank=True, related_name='assignments', verbose_name="Coding Exercises") 

    # Timestamps and User relations
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assignments')

    class Meta:
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        return f"{self.assignment_name} ({self.course})"


# Model for Student Assignment Attempt
class StudentAssignmentAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    # Scoring and feedback
    score = models.IntegerField(default=0, verbose_name="Score")
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

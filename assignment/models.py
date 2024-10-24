from django.db import models
from exercises.models import Exercise
from course.models import Course
from django.utils import timezone

class Assignment(models.Model):
    # General assignment information
    assignment_name = models.CharField(max_length=100, verbose_name="Assignment Name")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments', verbose_name="Course")

    # Content of the assignment (normal assignment)
    content = models.TextField(blank=True, null=True, verbose_name="Assignment Content") 

    # Coding exercises (optional, can have multiple exercises)
    coding_exercises = models.ManyToManyField(Exercise, blank=True, related_name='assignments', verbose_name="Coding Exercises") 

    # Scoring and feedback
    score = models.IntegerField(default=0, verbose_name="Score")
    note = models.TextField(blank=True, verbose_name="Notes")

    # Timeline
    start_date = models.DateTimeField(verbose_name="Start Date")
    end_date = models.DateTimeField(verbose_name="End Date")

    class Meta:
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        ordering = ['start_date']  # Orders assignments by their start date

    def __str__(self):
        return f"{self.assignment_name} ({self.course})"

    def is_active(self):
        """Check if the assignment is currently active based on its start and end dates."""
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def is_past_due(self):
        """Check if the assignment is past its end date."""
        return timezone.now() > self.end_date

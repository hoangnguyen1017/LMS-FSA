from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from course.models import Course
from exercises.models import Exercise
from quiz.models import Quiz, Question
from assignment.models import Assignment


class AssessmentType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Assessment Type"
        verbose_name_plural = "Assessment Types"

    def __str__(self):
        return self.type_name
    def save(self, *args, **kwargs):
        # Check for duplicates
        if AssessmentType.objects.filter(type_name=self.type_name).exists():
            raise ValidationError(_("This assessment type already exists."))
        super().save(*args, **kwargs)



class Assessment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments', verbose_name="Course")
    title = models.CharField(max_length=255)
    
    # Many-to-many relationships
    exercises = models.ManyToManyField(Exercise, related_name='assessments', blank=True)
    questions = models.ManyToManyField(Question, related_name='assessments', blank=True)

    # Foreign key to AssessmentType
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name='assessments')

    invited_count = models.IntegerField(default=0, verbose_name="Invited Count")
    assessed_count = models.IntegerField(default=0, verbose_name="Assessed Count")
    qualified_count = models.IntegerField(default=0, verbose_name="Qualified Count") 

    qualify_score = models.IntegerField(default=0, verbose_name="Qualify Score")
    total_score = models.IntegerField(default=0, verbose_name="Total Score")
    
    created_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assessments')

    class Meta:
        ordering = ['created_at', 'course']
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"

    def __str__(self):
        return f"{self.title} ({self.assessment_type}) - Due: {self.due_date}"

    def is_past_due(self):
        """Check if the due date has passed."""
        return self.due_date and timezone.now() > self.due_date


class StudentAssessmentAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    # Scoring and feedback
    score_quiz = models.IntegerField(default=0, verbose_name="Quiz Score")
    score_ass = models.IntegerField(default=0, verbose_name="Assignment Score")
    note = models.TextField(blank=True, null=True, verbose_name="Notes")

    # Timestamps and User relations
    attempt_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Assignment Attempt"
        verbose_name_plural = "Student Assignment Attempts"

    def __str__(self):
        return f"Attempt by {self.user} for {self.assessment}"

    def clean(self):
        # Ensure both scores are non-negative
        if self.score_quiz < 0:
            raise ValidationError({'score_quiz': _("Quiz score cannot be negative.")})
        if self.score_ass < 0:
            raise ValidationError({'score_ass': _("Assignment score cannot be negative.")})

    def save(self, *args, **kwargs):
        # Clean data before saving
        self.clean()
        super().save(*args, **kwargs)

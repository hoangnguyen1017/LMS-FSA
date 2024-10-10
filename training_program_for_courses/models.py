from django.db import models
from django.contrib.auth.models import User

class TrainingProgramCourse(models.Model):
    program_name = models.CharField(max_length=255, unique=True)
    program_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.program_name

class TrainingProgramCourseEnrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_program_for_courses_enrollments')
    program = models.ForeignKey(TrainingProgramCourse, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'program')

    def __str__(self):
        return f"{self.student} enrolled in {self.program}"


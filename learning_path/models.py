from django.db import models
from django.conf import settings
from course.models import Course

class LearningPath(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Step(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sequence = models.PositiveIntegerField()  # This defines the order of steps
    learning_path = models.ForeignKey(LearningPath, related_name='steps', on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, related_name='steps', blank=True)

    class Meta:
        ordering = ['sequence']  # Automatically order steps by their sequence number

    def __str__(self):
        return f"Step {self.sequence}: {self.title}"

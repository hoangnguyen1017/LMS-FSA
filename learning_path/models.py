from django.db import models
from django.conf import settings
from course.models import Course 

# Create your models here.
class LearningPath(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    courses = models.ManyToManyField(Course, related_name='learning_paths')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
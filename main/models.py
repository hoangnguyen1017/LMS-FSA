from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from role.models import Role  # Import the Role model

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='news_files/', blank=True, null=True)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='events_files/', blank=True, null=True)

    def __str__(self):
        return self.title


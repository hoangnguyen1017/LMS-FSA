from django.db import models
from user.models import User
from subject.models import Subject

# Create your models here.
class ProgressNotification(models.Model):    
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    # course = models.CharField(max_length=255)
    course = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    notification_message = models.CharField(max_length=255, blank=True, null=True)
    notification_date = models.DateTimeField(auto_now_add=True)
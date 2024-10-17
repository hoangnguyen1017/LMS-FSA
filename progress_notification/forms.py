from django import forms
from .models import ProgressNotification

# Form for creating and editing users
class ProgressNotificationForm(forms.ModelForm):
    class Meta:
        model = ProgressNotification
        fields = ['username', 'course', 'notification_message']

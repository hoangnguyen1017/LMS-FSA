from django import forms
from .models import CollaborationGroup
from subject.models import Subject
from user.models import User
class CollaborationGroupForm(forms.ModelForm):
    class Meta:
        model = CollaborationGroup
        fields = ['group_name', 'course']
        widgets = {
            'course': forms.Select(),  # Drop-down list for selecting subjects
        }
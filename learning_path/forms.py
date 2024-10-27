from django import forms
from .models import LearningPath, Step
from course.models import Course

class LearningPathForm(forms.ModelForm):
    class Meta:
        model = LearningPath
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['title', 'description', 'sequence', 'courses']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'sequence': forms.NumberInput(attrs={'class': 'form-control'}),
            'courses': forms.SelectMultiple(attrs={'class': 'form-control'}),  # Multi-select for courses
        }

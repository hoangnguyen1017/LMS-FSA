from django import forms
from .models import Assignment

from django import forms
from .models import Assignment, StudentAssignmentAttempt

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['assignment_name', 'course', 'content', 'coding_exercises']  # Updated fields
        widgets = {
            'assignment_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'coding_exercises': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
        }

class StudentAssignmentAttemptForm(forms.ModelForm):
    class Meta:
        model = StudentAssignmentAttempt
        fields = ['user', 'assignment', 'score', 'note']  # Updated fields
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'assignment': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean(self):
        """Ensure the score is within the defined range."""
        cleaned_data = super().clean()
        score = cleaned_data.get("score")

        if score is not None:
            if score < 0 or score > 100:  # Adjust the range as per your scoring system
                raise forms.ValidationError("Score must be between 0 and 100.")

        return cleaned_data


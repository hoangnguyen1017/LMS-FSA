from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['course', 'assignment_name', 'start_date', 'end_date']  # Thêm course
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'assignment_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
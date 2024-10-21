from django import forms
from .models import AssessmentType, Assessment, StudentAssessmentAttempt

class AssessmentTypeForm(forms.ModelForm):
    class Meta:
        model = AssessmentType
        fields = ['type_name']

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'course', 'assessment_type', 'total_score', 'due_date', 'exercises']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'assessment_type': forms.Select(attrs={'class': 'form-control'}),
            'total_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'exercises': forms.CheckboxSelectMultiple(),
        }


class AssessmentAttemptForm(forms.ModelForm):
    class Meta:
        model = StudentAssessmentAttempt
        fields = ['score_quiz', 'score_ass', 'note']

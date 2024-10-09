from django import forms
from .models import Quiz, Submission

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'course', 'category', 'due_date', 'attempts_allowed', 'grading_method']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'attempts_allowed': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['attempts_allowed'].widget.attrs.update({'min': 1})

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['submitted_file']

class GradingForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['grade']
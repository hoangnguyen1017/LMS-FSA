# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Quiz, Question, AnswerOption

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['course', 'quiz_title', 'quiz_description', 'total_marks', 'time_limit', 'start_datetime', 'end_datetime', 'attempts_allowed']
        widgets = {
            'course': forms.Select(),
            'time_limit': forms.NumberInput(attrs={'min': 1}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'attempts_allowed': forms.NumberInput(attrs={'min': '1'}), 
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'points']

class AnswerOptionForm(forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = ['option_text', 'is_correct']




# Formset for multiple questions
QuestionFormSet = inlineformset_factory(
    Quiz, Question, form=QuestionForm, extra=1, can_delete=True
)

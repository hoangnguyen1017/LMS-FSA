from django import forms
from .models import Question, Answer, Subject
from django.forms import modelformset_factory, inlineformset_factory

# Form for creating and editing questions
class QuestionForm(forms.ModelForm):
    METHOD_CHOICES = [
        ('essay', 'Essay'),
        ('multiple_choice', 'Multiple Choice'),
    ]
    method_answer = forms.ChoiceField(choices=METHOD_CHOICES, required=True)

    class Meta:
        model = Question
        fields = ['subject', 'category', 'subcategory', 'question_text']
        # If you need to specify the subject field explicitly:
        # widgets = {
        #     'subject': forms.Select(attrs={'class': 'form-control'}),
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question_text'].required = False
        self.fields['subject'].queryset = Subject.objects.all().order_by('name')
        self.fields['subject'].to_field_name = 'subject_id'  # Use subject_id for the value
        # If you need to update the queryset for the subject field:
        # self.fields['subject'].queryset = Subject.objects.all().order_by('name')

# Form for creating and editing answers
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']  # Changed from 'answer_text' to 'text'

# Formset for handling multiple answers per question, quán lý nhóm các form trong app
AnswerFormSet = inlineformset_factory(Question, Answer, form=AnswerForm, extra=1)

# Formset for handling multiple questions
QuestionFormSet = modelformset_factory(Question, form=QuestionForm, extra=1)


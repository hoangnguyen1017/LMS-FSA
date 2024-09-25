from django import forms
from .models import QuizQuestionAnswer

class QuizQuestionAnswerForm(forms.ModelForm):
    class Meta:
        model = QuizQuestionAnswer
        fields = ['question_description', 'answertext_1', 'answertext_2', 'answertext_3', 'answertext_4', 'correct_answer']


from .models import UserAnswer

class UserAnswerForm(forms.ModelForm):
    class Meta:
        model = UserAnswer
        fields = ['question','selected_answer']
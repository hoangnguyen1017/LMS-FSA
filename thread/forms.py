from django import forms
from .models import DiscussionThread,ThreadComments
from user.models import User  # Assuming you have a User model
from subject.models import Subject
class ThreadForm(forms.ModelForm):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), required=True, empty_label="Select a subject")

    class Meta:
        model = DiscussionThread
        fields = ['thread_title', 'thread_content', 'subject']

class CommentForm(forms.ModelForm):
    class Meta:
        model = ThreadComments
        fields = ['comment_text']
      
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import News, Event
from role.models import Role  # Import the Role model

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=True, empty_label="Select Role")
    first_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': ''}),
        label='Full Name' )
    class Meta:
        model = User
        fields = ['username', 'email','first_name', 'password1', 'password2', 'role']



class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'file']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date', 'file']
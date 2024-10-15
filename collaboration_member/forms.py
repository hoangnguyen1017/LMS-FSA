from django import forms
from .models import GroupMember

class GroupMemberForm(forms.ModelForm):
    class Meta:
        model = GroupMember
        fields = ['user']  # Assuming user is selected from a dropdown, you may customize this as needed

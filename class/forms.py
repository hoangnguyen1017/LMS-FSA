
from django import forms
from .models import ClassInfo,Student

class ClassInfoForm(forms.ModelForm):
    class Meta:
        model = ClassInfo
        fields = ['id_class', 'number_student', 'class_mentor']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id','class_info', 'first_name', 'last_name']
        widgets = {
            'class_info': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        } 
from django import forms
from .models import *
from user.models import User
#from ckeditor.widgets import CKEditorWidget

# Form for creating and editing courses

class CourseForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label="Select Creator")
    instructor = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label="Select Instructor")
    prerequisites = forms.ModelMultipleChoiceField(queryset=Course.objects.all(),required=False,widget=forms.CheckboxSelectMultiple)
    integer_field = forms.IntegerField(required=False)  # mới thêm
    tags = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}),
                           required=False)

    def clean_integer_field(self):
        data = self.cleaned_data.get('integer_field')
        if data == '':
            return None  # or handle as needed
        return data

    class Meta:
        model = Course
        fields = ['course_name', 'course_code', 'description', 'creator', 'instructor', 'prerequisites', 'tags']  # sửa lại

class SessionForm(forms.ModelForm):
    session_name = forms.CharField(max_length=50, required=False, label="Session Name")
    session_quantity = forms.IntegerField(min_value=1, required=False, label="Number of Sessions")
    class Meta:
        model = Session
        fields = ['name', 'order', 'course']

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = []

class CourseSearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False, label='Research Course')

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")


class CompletionForm(forms.ModelForm):
    class Meta:
        model = Completion
        fields = ['completed', 'material']


class ReadingMaterialForm(forms.ModelForm):
    #content = forms.CharField(widget=CKEditorWidget(config_name='default'))
    class Meta:
        model = ReadingMaterial
        fields = ['title', 'content', 'order']

class UploadFileForm(forms.Form):
    file = forms.FileField()

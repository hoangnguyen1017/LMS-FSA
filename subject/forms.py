from django import forms
from .models import Subject, Document, Video, Enrollment, Completion, ReadingMaterial
from django.contrib.auth.models import User

# Form for creating and editing subjects

class SubjectForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label="Select Creator")
    instructor = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label="Select Instructor")
    class Meta:
        model = Subject
        fields = ['name','subject_code', 'description', 'creator','instructor']

# Form cho việc thêm tài liệu
class DocumentForm(forms.ModelForm):
    doc_title = forms.CharField(label='Document Title', max_length=255,required=False)
    doc_file = forms.FileField(label='Upload Document',required=False)
    class Meta:
        model = Document
        fields = ['doc_title', 'doc_file']

# Form cho việc thêm video
class VideoForm(forms.ModelForm):
    vid_title = forms.CharField(label='Video Title', max_length=255,required=False)
    vid_file = forms.FileField(label='Upload Video',required=False)
    class Meta:
        model = Video
        fields = ['vid_title', 'vid_file']

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = []

class SubjectSearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=False, label='Research Subject')

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")


class CompletionForm(forms.ModelForm):
    class Meta:
        model = Completion
        fields = ['completed']


class ReadingMaterialForm(forms.ModelForm):
    class Meta:
        model = ReadingMaterial
        fields = ['title', 'content', 'subject']  # Include the subject if needed



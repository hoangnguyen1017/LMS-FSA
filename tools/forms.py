from django import forms
from .fields import MultipleFilesField

class ExcelUploadForm(forms.Form):
    files = MultipleFilesField(required=True)
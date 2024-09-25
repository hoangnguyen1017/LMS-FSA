# forms.py
from django import forms

class ExamGenerationForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")
    number_of_exams = forms.IntegerField(label="Number of Exams", min_value=1, max_value=100, initial=1)
    number_of_questions = forms.IntegerField(label="Number of Questions", min_value=1, max_value=100, initial=1)

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Upload Excel File')


class TxtUploadForm(forms.Form):
    txt_file = forms.FileField(label='Upload TXT File')

class MultipleTxtUploadForm(forms.Form):
    number_of_files = forms.IntegerField(min_value=1, label='Number of TXT Files')

    def __init__(self, *args, **kwargs):
        num_files = kwargs.pop('num_files', 1)
        super().__init__(*args, **kwargs)
        
        for i in range(num_files):
            self.fields[f'txt_file_{i}'] = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 10, 'placeholder': f'Content for TXT file {i + 1}'}),
                label=f'TXT File {i + 1}',
                required=False
            )
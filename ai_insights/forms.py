from django import forms
from .models import AIInsights

# Form for creating and editing users
class AI_InsightsForm(forms.ModelForm):
    class Meta:
        model = AIInsights
        fields = ['user', 'course', 'insight_text', 'insight_type']

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")

from django import forms
from .models import TrainingProgramCourse, TrainingProgramCourseEnrollment

# Form for creating and editing training programs
class TrainingProgramCourseForm(forms.ModelForm):
    class Meta:
        model = TrainingProgramCourse
        fields = ['program_name', 'program_code', 'description']

class TrainingProgramCourseEnrollmentForm(forms.ModelForm):
    class Meta:
        model = TrainingProgramCourseEnrollment
        fields = []
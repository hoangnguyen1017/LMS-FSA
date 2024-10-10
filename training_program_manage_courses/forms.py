from django import forms
from .models import TrainingProgramCourses, Course

class TrainingProgramCoursesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        program = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if program:
            courses = Course.objects.all()
            for course in courses:
                self.fields[f'course_{course.id}'] = forms.BooleanField(
                    label=course.name, required=False)
                self.fields[f'semester_{course.id}'] = forms.ChoiceField(
                    choices=[(i, f'Semester {i}') for i in range(1, 10)],
                    required=False)

    def save(self, program):
        TrainingProgramCourses.objects.filter(program=program).delete()
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('course_') and value:
                id = int(field_name.split('_')[1])
                semester = self.cleaned_data.get(f'semester_{id}')
                course = Course.objects.get(sid=id)
                TrainingProgramCourses.objects.create(
                    program=program, course=course, semester=semester)

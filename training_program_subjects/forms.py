from django import forms
from .models import TrainingProgramSubjects, Subject

class TrainingProgramSubjectsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        program = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        if program:
            subjects = Subject.objects.all()
            for subject in subjects:
                self.fields[f'subject_{subject.id}'] = forms.BooleanField(
                    label=subject.name, required=False)
                self.fields[f'semester_{subject.id}'] = forms.ChoiceField(
                    choices=[(i, f'Semester {i}') for i in range(1, 10)],
                    required=False)

    def save(self, program):
        TrainingProgramSubjects.objects.filter(program=program).delete()
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('subject_') and value:
                id = int(field_name.split('_')[1])
                semester = self.cleaned_data.get(f'semester_{id}')
                subject = Subject.objects.get(sid=id)
                TrainingProgramSubjects.objects.create(
                    program=program, subject=subject, semester=semester)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import TrainingProgram, TrainingProgramEnrollment
from .forms import TrainingProgramForm, TrainingProgramEnrollmentForm
from training_program_subjects.models import TrainingProgramSubjects, Subject  # Add Subject here
from training_program_subjects.forms import TrainingProgramSubjectsForm
from module_group.models import ModuleGroup
# Home view
def home(request):
    return render(request, 'home.html')

# Manage subjects in a training program
def manage_subjects(request, program_id):
    program = get_object_or_404(TrainingProgram, pk=program_id)
    if request.method == 'POST':
        form = TrainingProgramSubjectsForm(request.POST, instance=program)
        if form.is_valid():
            TrainingProgramSubjects.objects.filter(program=program).delete()
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('subject_') and value:
                    id = int(field_name.split('_')[1])
                    semester = form.cleaned_data.get(f'semester_{id}')
                    subject = Subject.objects.get(id=id)
                    TrainingProgramSubjects.objects.create(
                        program=program, subject=subject, semester=semester)
            return redirect('training_program:training_program_list')
    else:
        form = TrainingProgramSubjectsForm(instance=program)

    return render(request, 'manage_subjects.html', {'form': form, 'program': program})

# TrainingProgram views
def training_program_list(request):
    module_groups = ModuleGroup.objects.all()
    programs = TrainingProgram.objects.all()
    return render(request, 'training_program_list.html', {
        'programs': programs,
        'module_groups': module_groups,
        })

def training_program_add(request):
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('training_program:training_program_list')
    else:
        form = TrainingProgramForm()
    return render(request, 'training_program_form.html', {'form': form})

def training_program_edit(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        form = TrainingProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect('training_program:training_program_list')
    else:
        form = TrainingProgramForm(instance=program)
    return render(request, 'training_program_form.html', {'form': form})

def training_program_delete(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        program.delete()
        return redirect('training_program:training_program_list')
    return render(request, 'training_program_confirm_delete.html', {'program': program})

@login_required
def training_program_enroll(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    if request.method == 'POST':
        form = TrainingProgramEnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = request.user
            enrollment.program = program
            enrollment.save()
            return redirect('training_program:training_program_list')
    else:
        form = TrainingProgramEnrollmentForm()
    return render(request, 'training_program_enroll.html', {'form': form, 'program': program})

@login_required
def training_program_unenroll(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    try:
        enrollment = TrainingProgramEnrollment.objects.get(student=request.user, program=program)
        enrollment.delete()
    except TrainingProgramEnrollment.DoesNotExist:
        pass
    return redirect('training_program:training_program_list')

@login_required
def users_enrolled(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)
    enrolled_users = TrainingProgramEnrollment.objects.filter(program=program).select_related('student')
    return render(request, 'users_enrolled.html', {
        'program': program,
        'enrolled_users': enrolled_users,
    })

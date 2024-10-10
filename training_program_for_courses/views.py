from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import TrainingProgramCourse, TrainingProgramCourseEnrollment
from .forms import TrainingProgramCourseForm, TrainingProgramCourseEnrollmentForm
from training_program_manage_courses.models import TrainingProgramCourses, Course  # Add Course here
from training_program_manage_courses.forms import TrainingProgramCoursesForm
from module_group.models import ModuleGroup
from course.models import Completion, SessionCompletion

# Home view
def home(request):
    return render(request, 'home.html')

# Manage courses in a training program
def manage_courses(request, program_id):
    program = get_object_or_404(TrainingProgramCourse, pk=program_id)
    if request.method == 'POST':
        form = TrainingProgramCoursesForm(request.POST, instance=program)
        if form.is_valid():
            TrainingProgramCourses.objects.filter(program=program).delete()
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('course_') and value:
                    id = int(field_name.split('_')[1])
                    semester = form.cleaned_data.get(f'semester_{id}')
                    course = Course.objects.get(id=id)
                    TrainingProgramCourses.objects.create(
                        program=program, course=course, semester=semester)
            return redirect('training_program_for_courses:training_program_list')
    else:
        form = TrainingProgramCoursesForm(instance=program)

    return render(request, 'manage_courses.html', {'form': form, 'program': program})

# TrainingProgram views
def training_program_list(request):
    programs = TrainingProgramCourse.objects.all()
    user_completion_data = []

    for program in programs:
        total_courses = TrainingProgramCourses.objects.filter(program=program).count()
        completed_courses = SessionCompletion.objects.filter(
            course__in=program.trainingprogramcourses_set.all().values_list('course', flat=True),
            completed=True,
            course__enrollment__student=request.user
        ).values('course').distinct().count()

        completion_percent = (completed_courses / total_courses) * 100 if total_courses > 0 else 0
        user_completion_data.append({
            'program': program,
            'completion_percent': completion_percent
        })

    return render(request, 'training_program_course_list.html', {
        'user_completion_data': user_completion_data,
    })

def training_program_add(request):
    if request.method == 'POST':
        form = TrainingProgramCourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('training_program_for_courses:training_program_list')
    else:
        form = TrainingProgramCourseForm()
    return render(request, 'training_program_course_form.html', {'form': form})

def training_program_edit(request, pk):
    program = get_object_or_404(TrainingProgramCourse, pk=pk)
    if request.method == 'POST':
        form = TrainingProgramCourseForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect('training_program_for_courses:training_program_list')
    else:
        form = TrainingProgramCourseForm(instance=program)
    return render(request, 'training_program_course_form.html', {'form': form})

def training_program_delete(request, pk):
    program = get_object_or_404(TrainingProgramCourse, pk=pk)
    if request.method == 'POST':
        program.delete()
        return redirect('training_program_for_courses:training_program_list')
    return render(request, 'training_program_course_confirm_delete.html', {'program': program})

@login_required
def training_program_enroll(request, pk):
    program = get_object_or_404(TrainingProgramCourse, pk=pk)
    if request.method == 'POST':
        form = TrainingProgramCourseEnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = request.user
            enrollment.program = program
            enrollment.save()
            return redirect('training_program_for_courses:training_program_list')
    else:
        form = TrainingProgramCourseEnrollmentForm()
    return render(request, 'training_program_course_enroll.html', {'form': form, 'program': program})

@login_required
def training_program_unenroll(request, pk):
    program = get_object_or_404(TrainingProgramCourse, pk=pk)
    try:
        enrollment = TrainingProgramCourseEnrollment.objects.get(student=request.user, program=program)
        enrollment.delete()
    except TrainingProgramCourseEnrollment.DoesNotExist:
        pass
    return redirect('training_program_for_courses:training_program_list')

@login_required
def users_enrolled(request, pk):
    program = get_object_or_404(TrainingProgramCourse, pk=pk)
    enrolled_users = TrainingProgramCourseEnrollment.objects.filter(program=program).select_related('student')

    # Calculate completion percentage for each user
    user_completion_data = []
    total_courses = TrainingProgramCourses.objects.filter(program=program).count()

    for enrollment in enrolled_users:
        # Get all courses in the program
        courses_in_program = program.trainingprogramcourses_set.all().values_list('course', flat=True)

        # Get all completions for the user in these courses
        completed_courses = SessionCompletion.objects.filter(
            course__in=courses_in_program,
            completed=True,
            course__enrollment__student=enrollment.student
        ).values('course').distinct().count()

        completion_percent = (completed_courses / total_courses) * 100 if total_courses > 0 else 0
        user_completion_data.append({
            'user': enrollment.student,
            'completion_percent': completion_percent
        })

    return render(request, 'users_enrolled_training_course.html', {
        'program': program,
        'user_completion_data': user_completion_data,
    })

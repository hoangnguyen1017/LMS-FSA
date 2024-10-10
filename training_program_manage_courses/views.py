from django.shortcuts import render, get_object_or_404, redirect
from .models import TrainingProgramCourse, Course, TrainingProgramCourses
from .forms import TrainingProgramCoursesForm

# Create your views here.
def manage_courses(request, program_id):
    program = get_object_or_404(TrainingProgramCourse, pk=program_id)
    if request.method == 'POST':
        form = TrainingProgramCoursesForm(request.POST, instance=program)
        if form.is_valid():
            form.save(program)
            return redirect('training_program_for_courses:training_program_list')
    else:
        form = TrainingProgramCoursesForm(instance=program)
    return render(request, 'manage_courses.html', {'form': form, 'program': program})

def view_courses(request, program_id):
    program = get_object_or_404(TrainingProgramCourse, pk=program_id)
    courses = TrainingProgramCourses.objects.filter(program=program).order_by('semester')
    return render(request, 'view_courses.html', {'program': program, 'courses': courses})

def training_program_view(request, pk):
    program = get_object_or_404(TrainingProgramCourse, pk=pk)
    return render(request, 'training_program_view.html', {'program': program})


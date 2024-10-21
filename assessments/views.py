from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from course.models import Course
from .models import Assessment, AssessmentType, StudentAssessmentAttempt
from .forms import AssessmentForm, AssessmentAttemptForm
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .forms import AssessmentForm  # Ensure you have a form for the assessment
from .models import Assessment, Exercise



def assessment_edit(request, pk):
    assessment = get_object_or_404(Assessment, id=pk)
    exercises = Exercise.objects.all()  # Fetch all available exercises
    selected_exercises = assessment.exercises.values_list('id', flat=True)  # Fetch selected exercises for the assessment

    if request.method == "POST":
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            # Handle saving associated exercises (if applicable)
            selected_ids = request.POST.getlist('exercises')
            assessment.exercises.set(selected_ids)  # Update the associated exercises
            assessment.save()
            messages.success(request, 'The assessment has been successfully saved.')  # Add a success message
            return redirect('assessment:assessment_edit', pk=pk)  # Redirect to the same edit page to see the message
    else:
        form = AssessmentForm(instance=assessment)

    return render(request, 'assessment/assessment_edit.html', {
        'form': form,
        'assessment': assessment,
        'exercises': exercises,
        'selected_exercises': selected_exercises,
    })



@login_required
def assessment_list(request):
    #quizzes = Quiz.objects.select_related('course').annotate(question_count=Count('questions')).all().order_by('-created_at')
    courses = Course.objects.all().order_by('course_name')
    assessments = Assessment.objects.all().order_by('created_at')

    # Lọc quiz dựa trên subject được chọn
    selected_course = request.GET.get('course', '')
    if selected_course:
        assessments = assessments.filter(course__id=selected_course)
  
    
    # Dynamically calculate exercise and question counts for each assessment
    assessments_with_counts = []
    for assessment in assessments:
        # Assuming you have related models for exercises and questions
        exercise_count = assessment.exercises.count()  # Assuming 'exercises' is a related field
        question_count = assessment.questions.count()  # Assuming 'questions' is a related field in exercises
        assessments_with_counts.append({
            'selected_course': selected_course,
            'assessment': assessment,
            'exercise_count': exercise_count,
            'question_count': question_count,
        })

    # Pass the assessments with their exercise and question counts to the template
    return render(request, 'assessment/assessment_list.html', {
        'courses': courses,
        'assessments_with_counts': assessments_with_counts,
    })


def get_exercise_content(request, exercise_id):
    exercise = Exercise.objects.get(id=exercise_id)
    return JsonResponse({
        'title': exercise.title,
        'content': exercise.description  
    })


@login_required
def assessment_create(request):
    query = request.GET.get('search', '')
    exercises = Exercise.objects.filter(title__icontains=query)  # Filter exercises based on search query
    paginator = Paginator(exercises, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        selected_exercises = request.POST.getlist('exercises')  # Get selected exercises from form

        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.created_by = request.user
            assessment.save()
            form.save_m2m()  # Save ManyToMany relationships

            # Add selected exercises to the assessment
            for exercise_id in selected_exercises:
                exercise = get_object_or_404(Exercise, id=exercise_id)
                assessment.exercises.add(exercise)  # Add the exercises to assessment

            messages.success(request, 'Assessment created successfully with exercises!')
            return redirect('assessment:assessment_list')

    else:
        form = AssessmentForm()

    return render(request, 'assessment/add_exercise.html', {
        'form': form,
        'exercises': exercises,
        'page_obj': page_obj,
        'selected_exercises': [],  # Initially no exercises selected
        'search': query
    })


def save_assessment(request):
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            form.save()
            # Return a JSON response indicating success
            return JsonResponse({'status': 'success'})
        else:
            # Return a JSON response with the form errors
            return JsonResponse({'status': 'error', 'message': form.errors.as_json()})
    
    # If not POST, return a 404
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=404)

def assessment_create1(request):
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.created_by = request.user
            assessment.save()
            form.save_m2m()  # Save ManyToMany relationships
            messages.success(request, 'Assessment created successfully!')
            return redirect('assessment:assessment_list')
    else:
        form = AssessmentForm()
    return render(request, 'assessment/assessment_form.html', {'form': form})
    

@login_required
def assessment_detail(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    return render(request, 'assessment/assessment_detail.html', {'assessment': assessment})

@login_required
def student_assessment_attempt(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    if request.method == 'POST':
        form = AssessmentAttemptForm(request.POST)
        if form.is_valid():
            attempt = form.save(commit=False)
            attempt.user = request.user
            attempt.assessment = assessment
            attempt.save()
            messages.success(request, 'Your attempt has been recorded.')
            return redirect('assessment:assessment_detail', pk=assessment.id)
    else:
        form = AssessmentAttemptForm()
    return render(request, 'assessment/assessment_attempt_form.html', {'form': form, 'assessment': assessment})

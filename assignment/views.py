from django.shortcuts import render,get_object_or_404,redirect
from exercises.models import Exercise
from .models import Assignment
from .forms import AssignmentForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.core.paginator import Paginator

# Create your views here.
def assignment_list(request):
    assignments = Assignment.objects.all()
    return render(request, 'assignment_list.html', {'assignments': assignments})

def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    exercises = assignment.coding_exercises.all()  
    return render(request, 'assignment_detail.html', {'assignment': assignment, 'exercises': exercises})

def assignment_add(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            return redirect('assignment:assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm()
    return render(request, 'assignment_form.html', {'form': form})

def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            return redirect('assignment:assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'assignment_form.html', {'form': form})

def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        return redirect('assignment:assignment_list')
    return render(request, 'assignment_confirm_delete.html', {'assignment': assignment})


def assignment_add_coding_exercise(request, pk):
    query = request.GET.get('search', '')
    exercises = Exercise.objects.filter(title__icontains=query)
    paginator = Paginator(exercises, 5)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  

    assignment = get_object_or_404(Assignment, pk=pk)
    selected_exercises = assignment.coding_exercises.all()

    return render(request, 'assignment_add_coding_exercise.html', {
        'page_obj': page_obj,  
        'assignment': assignment,
        'selected_exercises': selected_exercises,
        'search': query  
    })
    
@csrf_exempt
def save_assignment_exercises(request, assignment_id):
    if request.method == 'POST':
        try:
            assignment = get_object_or_404(Assignment, id=assignment_id)
            data = json.loads(request.body)
            selected_exercises_ids = data.get('exercises', [])
            assignment.coding_exercises.clear()

            for exercise_id in selected_exercises_ids:
                exercise = get_object_or_404(Exercise, id=exercise_id)
                assignment.coding_exercises.add(exercise)

            assignment.save()  

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)









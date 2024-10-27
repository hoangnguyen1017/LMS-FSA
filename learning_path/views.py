from django.shortcuts import render, redirect, get_object_or_404
from .models import LearningPath, Step
from .forms import LearningPathForm, StepForm

# Learning Path Views
def learning_path_list(request):
    learning_paths = LearningPath.objects.all()
    return render(request, 'learning_path/list.html', {'learning_paths': learning_paths})

def learning_path_add(request):
    if request.method == 'POST':
        form = LearningPathForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_path:learning_path_list')
    else:
        form = LearningPathForm()
    return render(request, 'learning_path/form.html', {'form': form})

def learning_path_edit(request, pk):
    learning_path = get_object_or_404(LearningPath, pk=pk)
    if request.method == 'POST':
        form = LearningPathForm(request.POST, instance=learning_path)
        if form.is_valid():
            form.save()
            return redirect('learning_path:learning_path_list')
    else:
        form = LearningPathForm(instance=learning_path)
    return render(request, 'learning_path/form.html', {'form': form})

def learning_path_delete(request, pk):
    learning_path = get_object_or_404(LearningPath, pk=pk)
    if request.method == 'POST':
        learning_path.delete()
        return redirect('learning_path:learning_path_list')
    return render(request, 'learning_path/confirm_delete.html', {'learning_path': learning_path})

# Step Views
def step_list(request, learning_path_id):
    learning_path = get_object_or_404(LearningPath, pk=learning_path_id)
    steps = learning_path.steps.all()
    return render(request, 'step/list.html', {'steps': steps, 'learning_path': learning_path})

from django.shortcuts import render, redirect, get_object_or_404
from .models import LearningPath, Step
from .forms import StepForm

def step_add(request, learning_path_id):
    learning_path = get_object_or_404(LearningPath, pk=learning_path_id)
    if request.method == 'POST':
        form = StepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.learning_path = learning_path  # Assign the learning path to the step
            step.save()
            form.save_m2m()  # Save many-to-many relationships for courses
            return redirect('learning_path:step_list', learning_path_id=learning_path.id)
    else:
        form = StepForm()
    return render(request, 'step/form.html', {'form': form, 'learning_path': learning_path})


def step_edit(request, learning_path_id, pk):
    step = get_object_or_404(Step, pk=pk)
    if request.method == 'POST':
        form = StepForm(request.POST, instance=step)
        if form.is_valid():
            step = form.save(commit=False)  # Save without committing to handle M2M
            step.learning_path_id = learning_path_id  # Optional, ensure correct learning path
            step.save()
            form.save_m2m()  # Save M2M relationships after saving the instance
            return redirect('learning_path:step_list', learning_path_id=learning_path_id)
    else:
        form = StepForm(instance=step)
    return render(request, 'step/form.html', {'form': form, 'learning_path': step.learning_path})


def step_delete(request, learning_path_id, pk):
    step = get_object_or_404(Step, pk=pk)
    if request.method == 'POST':
        step.delete()
        return redirect('learning_path:step_list', learning_path_id=learning_path_id)
    return render(request, 'step/confirm_delete.html', {'step': step})

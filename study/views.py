from django.shortcuts import render, get_object_or_404, redirect
from .models import Study
from .forms import StudyForm
#Create your views here.
def study_list(request):
    studies = Study.objects.all()
    return render(request , 'study_list.html' , {'studies': studies})

def study_add(request):
    if request.method == 'POST':
        form = StudyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('study:study_list')
    else:
        form = StudyForm()
    return render(request, 'study_form.html', {'form': form})
def study_edit(request, pk):
    study = get_object_or_404(Study, pk=pk)
    if request.method == 'POST':
        form = StudyForm(request.POST, request.FILES, instance=study)
        if form.is_valid():
            form.save()
            return redirect('study:study_list')
    else:
        form = StudyForm(instance=study)
    return render(request, 'study_form.html', {'form': form})

def study_delete(request, pk):
    study = get_object_or_404(Study, pk=pk)
    if request.method == 'POST':
        study.delete()
        return redirect('study:study_list')
    return render(request, 'study_confirm_delete.html', {'study': study})


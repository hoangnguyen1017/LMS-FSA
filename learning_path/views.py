from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import LearningPath
from .forms import LearningPathForm

# List and Search View
class LearningPathListView(ListView):
    model = LearningPath
    template_name = 'learning_path/learning_path_list.html'
    context_object_name = 'learning_paths'
    
    def get_queryset(self):
        query = self.request.GET.get('search')
        if query:
            return LearningPath.objects.filter(title__icontains=query)
        return LearningPath.objects.all()

# Create View
class LearningPathCreateView(CreateView):
    model = LearningPath
    form_class = LearningPathForm
    template_name = 'learning_path/learning_path_form.html'
    success_url = reverse_lazy('learning_path:learning_path_list')

# Update View
class LearningPathUpdateView(UpdateView):
    model = LearningPath
    form_class = LearningPathForm
    template_name = 'learning_path/learning_path_form.html'
    success_url = reverse_lazy('learning_path:learning_path_list')



class LearningPathDetailView(DetailView):
    model = LearningPath
    template_name = 'learning_path/learning_path_detail.html'
    context_object_name = 'learning_path'


# Delete View
class LearningPathDeleteView(DeleteView):
    model = LearningPath
    template_name = 'learning_path/learning_path_confirm_delete.html'
    success_url = reverse_lazy('learning_path:learning_path_list')

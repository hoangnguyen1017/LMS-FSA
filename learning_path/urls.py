from django.urls import path
from .views import (
    LearningPathListView,
    LearningPathCreateView,
    LearningPathUpdateView,
    LearningPathDeleteView,
    LearningPathDetailView,
)

app_name = 'learning_path'

urlpatterns = [
    path('', LearningPathListView.as_view(), name='learning_path_list'),
    path('add/', LearningPathCreateView.as_view(), name='learning_path_add'),
    path('<int:pk>/', LearningPathDetailView.as_view(), name='learning_path_detail'),  # Detail view URL
    path('<int:pk>/edit/', LearningPathUpdateView.as_view(), name='learning_path_edit'),
    path('<int:pk>/delete/', LearningPathDeleteView.as_view(), name='learning_path_delete'),
]

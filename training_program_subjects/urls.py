from django.urls import path
from . import views

app_name = 'training_program_subject'
urlpatterns = [
    path('training_program_subjects/<int:program_id>/', views.manage_subjects, name='training_program_subjects_form'),
]

#path('training_program_subjects/<int:program_id>/', views.manage_subjects, name='training_program_subjects_form'),
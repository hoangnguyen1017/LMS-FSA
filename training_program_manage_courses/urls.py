from django.urls import path
from . import views

app_name = 'training_program_manage_courses'
urlpatterns = [
    path('training_program_courses/', views.manage_courses, name='training_program_courses_form'),
    path('view_courses/', views.view_courses, name='view_courses'),  # Add this line
]

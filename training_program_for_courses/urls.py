from django.urls import path
from . import views
from training_program_manage_courses.views import view_courses  # Add this import

app_name = 'training_program_for_courses'
urlpatterns = [
    path('training_programs/', views.training_program_list, name='training_program_list'),
    path('training_programs/create/', views.training_program_add, name='training_program_add'),
    path('training_programs/edit/<int:pk>/', views.training_program_edit, name='training_program_edit'),
    path('training_programs/delete/<int:pk>/', views.training_program_delete, name='training_program_delete'),
    path('training_programs/<int:program_id>/manage_courses/', views.manage_courses, name='training_program_manage_courses'),
    path('training_programs_courses/<int:program_id>/view_courses/', view_courses, name='training_program_view_courses'),
    path('enroll/<int:pk>/', views.training_program_enroll, name='training_program_enroll'),
    path('unenroll/<int:pk>/', views.training_program_unenroll, name='training_program_unenroll'),
    path('<int:pk>/users_enrolled/', views.users_enrolled, name='users_enrolled'),
]

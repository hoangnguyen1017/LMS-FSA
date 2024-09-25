

from django.urls import path
from . import views
app_name = 'class'
urlpatterns = [
    path('add/', views.add_class, name='add_class'),
    path('list/', views.class_list, name='class_list'),
    path('edit/<int:pk>/', views.class_edit, name='class_edit'),
    path('delete/<int:pk>/', views.class_delete, name='class_delete'),
    path('add_student/', views.add_student, name='add_student'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
]

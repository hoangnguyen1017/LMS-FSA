from django.urls import path
from . import views

app_name = 'study'
urlpatterns = [
    path('', views.study_list, name='study_list'),
    path('add/', views.study_add, name='study_add'),
    path('edit/<int:pk>/', views.study_edit, name='study_edit'),
    path('delete/<int:pk>/', views.study_delete, name='study_delete'),
]

# quiz/urls.py
from django.urls import path
from . import views

app_name = 'quiz'



urlpatterns = [
    path('', views.quiz_home, name='quiz_home'),
    path('add/', views.add_question_answer, name='add_question_answer'),
    path('edit/<int:pk>/', views.edit_question_answer, name='edit_question_answer'),
    path('delete/<int:pk>/', views.delete_question_answer, name='delete_question_answer'),
    path('take-quiz/', views.take_quiz, name='take_quiz'),
    path('grading/', views.quiz_grading_list, name='quiz_grading_list'),
]

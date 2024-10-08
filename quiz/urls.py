# urls.py
from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('add/', views.quiz_create, name='quiz_create'),
    path('edit/<int:quiz_id>/', views.quiz_edit, name='quiz_edit'),
    path('delete/<int:quiz_id>/', views.quiz_delete, name='quiz_delete'),
    
    path('<int:quiz_id>/question/', views.quiz_question_list, name='quiz_question_list'),
    path('<int:quiz_id>/question/add/', views.add_question, name='add_question'),
    path('<int:quiz_id>/questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),

    path('question/<int:question_id>/answers/', views.answer_list, name='answer_list'),
    path('questions/<int:question_id>/add_answer/', views.add_answer, name='add_answer'),
    path('answers/edit/<int:answer_id>/', views.answer_edit, name='answer_edit'),  
    path('answers/delete/<int:answer_id>/', views.answer_delete, name='answer_delete'),

    path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('<int:quiz_id>/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    
    path('<int:quiz_id>/import/', views.import_quiz, name='import_quiz'),
    path('<int:quiz_id>/export/', views.export_quiz, name='export_quiz'),
]

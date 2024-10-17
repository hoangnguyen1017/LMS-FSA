from django.urls import include, path
from . import views

app_name = 'assessment'

urlpatterns = [
    path('', views.assessement_list, name='assessment_list'),
    path('quiz/', include('quiz.urls')),  
    path('exercises/', include('exercises.urls')),
    # path('add/', views.AssessmentCreateView.as_view(), name='assessment_add'),
    # path('<int:pk>/edit/', views.AssessmentUpdateView.as_view(), name='assessment_edit'),
    # path('<int:pk>/delete/', views.AssessmentDeleteView.as_view(), name='assessment_delete'),
    # path('import/', views.AssessmentImportView.as_view(), name='assessment_import'),
    # path('export/', views.AssessmentExportView.as_view(), name='assessment_export'),
]

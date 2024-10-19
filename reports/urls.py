from django.urls import path
from . import views
app_name = 'reports'
urlpatterns = [
    path('dashboard/', views.report_dashboard, name='report_dashboard'),  # Dashboard
    path('individual/<int:user_id>/', views.individual_progress_report, name='individual_progress_report'),
    path('course/<int:course_id>/', views.course_progress_report, name='course_progress_report'),
    path('overall/', views.overall_progress_report, name='overall_progress_report'),
    path('top-performers/', views.top_performers_report, name='top_performers_report'),
    path('at-risk/', views.at_risk_students_report, name='at_risk_students_report'),
    path('last-accessed/', views.last_accessed_report, name='last_accessed_report'),
]


from django.urls import path
from . import views
app_name = 'analytics_report'

urlpatterns = [
    path('', views.analytics_report_list, name='analytics_report_list'),
    path('/<int:pk>/', views.analytics_report_detail, name='analytics_report_detail'),
    path('/create/', views.analytics_report_add, name='analytics_report_add'),
    path('/<int:pk>/edit/', views.analytics_report_edit, name='analytics_report_edit'),
    path('/<int:pk>/delete/', views.analytics_report_delete, name='analytics_report_delete'),
]

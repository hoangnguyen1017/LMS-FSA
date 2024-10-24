from django.urls import path
from . import views
app_name = 'progress_notification'

urlpatterns = [
    path('progress_notification/', views.progress_notification_list, name='progress_notification_list'),
    path('progress_notification/<int:id>/', views.progress_notification_detail, name='progress_notification_detail'),
    path('progress_notification/create/', views.progress_notification_add, name='progress_notification_add'),
    path('progress_notification/edit/<int:id>/', views.progress_notification_edit, name='progress_notification_edit'),
    path('progress_notification/delete/<int:id>/', views.progress_notification_delete, name='progress_notification_delete'),
]

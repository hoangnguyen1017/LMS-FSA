from django.urls import path
from . import views

app_name = 'user_progress'

urlpatterns = [
    path('',views.progress_list, name='progress_list')
]
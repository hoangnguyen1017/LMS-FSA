from django.urls import path
from . import views

appname = 'user_summary'

urlpatterns = [
    path('', views.user_summary, name='user_summary'),
]

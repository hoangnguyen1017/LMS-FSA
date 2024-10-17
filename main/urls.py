from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Import your views from the main app

app_name = 'main'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'),  # Example protected view
    
]

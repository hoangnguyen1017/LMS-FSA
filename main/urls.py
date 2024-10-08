
# main/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView


app_name = 'main'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register_view, name='register'), 
    path('', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='main:login'), name='logout'),
    path('accounts/login/', views.login_view, name='login'),

]

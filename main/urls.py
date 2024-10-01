from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Import your views from the main app

app_name = 'main'

urlpatterns = [
    # Your other URL patterns
    path('', views.home, name='home'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit/', views.dashboard_edit, name='dashboard_edit'),
    path('news/add/', views.news_add, name='news_add'),
    path('news/edit/<int:pk>/', views.news_edit, name='news_edit'),
    path('event/add/', views.event_add, name='event_add'),
    path('event/edit/<int:pk>/', views.event_edit, name='event_edit'),
    path('delete-news/<int:pk>/', views.delete_news, name='delete_news'),
    path('delete-event/<int:pk>/', views.delete_event, name='delete_event'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail')
]


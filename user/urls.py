from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    # path('accounts/profile/', views.profile_view, name='profile'),
    path('profile/', views.profile_view, name='profile'),  # Profile view URL
    path('users/', views.user_list, name='user_list'),  # New URL pattern
]

from django.urls import path
from . import views

app_name = 'thread'

urlpatterns = [
    path('threads/', views.thread_list, name='thread_list'),
    path('threads/create/', views.createThread, name='create_thread'),
    path('threads/update/<int:pk>/', views.updateThread, name='update_thread'),
    path('threads/delete/<int:pk>/', views.deleteThread, name='delete_thread'),
    path('threads/detail/<int:pk>',views.thread_detail, name= 'thread_detail'),
    path('threads/detail/<int:pk>/comments/add/', views.add_comment, name='add_comment'),
    path('threads/detail/<int:pk>/comments/<int:comment_id>/edit/', views.update_comment, name='update_comment'),
    path('threads/detail/<int:pk>/comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('moderation_warning/', views.moderation_warning, name='moderation_warning'),
]

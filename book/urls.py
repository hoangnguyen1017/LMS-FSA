from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.book_search_view, name='book_search'),
    path('<str:book_id>/', views.book_detail_view, name='book_detail'),
]
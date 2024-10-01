from django.urls import path
from . import views

app_name = 'category'
urlpatterns = [
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_add, name='category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    path('subcategories/create/', views.category_add, name='subcategory_add'),
    path('subcategories/edit/<int:pk>/', views.subcategory_edit, name='subcategory_edit'),
    path('subcategories/delete/<int:pk>/', views.subcategory_delete, name='subcategory_delete'),  # New URL for subcategory deletion
]

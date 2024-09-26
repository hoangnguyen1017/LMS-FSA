from django.urls import path
from . import views

app_name = 'subject'
urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('add/', views.subject_add, name='subject_add'),
    path('edit/<int:pk>/', views.subject_edit, name='subject_edit'),
    path('subjects/delete/<int:pk>/', views.subject_delete, name='subject_delete'),
    path('subject/enroll/<int:pk>/', views.subject_enroll, name='subject_enroll'),
    path('unenroll/<int:pk>/', views.subject_unenroll, name='subject_unenroll'),
    path('resources/', views.resource_library, name='resource_library'),
    path('<int:pk>/detail/', views.subject_detail, name='subject_detail'),
    path('<int:pk>/enrolled/', views.users_enrolled, name='users_enrolled'),
    path('search/', views.course_search, name='course_search'),
    path('download/<str:file_type>/<int:file_id>/', views.file_download, name='file_download'),
    path('<int:pk>/content/', views.subject_content, name='subject_content'),
    path('<int:pk>/content/edit/', views.subject_content_edit, name='subject_content_edit'),
    path('export/', views.export_subject, name='export_subject'),
    path('import/', views.import_modules, name='import_modules'),
    path('subject/<int:pk>/toggle_publish/', views.toggle_publish, name='toggle_publish'),
]

from django.urls import path
from . import views

app_name = 'course'
urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('add/', views.course_add, name='course_add'),
    path('edit/<int:pk>/', views.course_edit, name='course_edit'),
    path('courses/delete/<int:pk>/', views.course_delete, name='course_delete'),
    path('course/enroll/<int:pk>/', views.course_enroll, name='course_enroll'),
    path('unenroll/<int:pk>/', views.course_unenroll, name='course_unenroll'),
    path('<int:pk>/detail/', views.course_detail, name='course_detail'),
    path('<int:pk>/enrolled/', views.users_enrolled, name='users_enrolled'),
    path('search/', views.course_search, name='course_search'),
    path('<int:pk>/content/<int:session_id>/', views.course_content, name='course_content'),
    path('<int:pk>/content/edit/<int:session_id>/', views.course_content_edit, name='course_content_edit'),
    path('export/', views.export_course, name='export_course'),
    path('import/', views.import_courses, name='import_course'),
    path('course/<int:pk>/toggle_publish/', views.toggle_publish, name='toggle_publish'),
    path('<int:pk>/toggle-completion/', views.toggle_completion, name='toggle_completion'),
    path('edit/<int:pk>/reorder/<int:session_id>/', views.reorder_course_materials, name='reorder_course_materials'),
    path('reading-material/<int:id>/', views.reading_material_detail, name='reading_material_detail'),
    path('<int:pk>/generate-certificate/', views.generate_certificate_png, name='generate_certificate'),
]



from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('main.urls')),  # Include the URLs of the main app

    path('module_group/', include('module_group.urls')),
    path('user/', include('user.urls')),             # For user-related views
    path('user_module/', include('user_module.urls')), # For user-module assignments
    path('category/', include('category.urls')),
    path('question/', include('question.urls')),
    path('role/', include('role.urls')),
    path('subject/', include('subject.urls')),
    path('training_program/', include('training_program.urls')),
    path('training_program_subjects/', include('training_program_subjects.urls')),
    path('feedback/', include('feedback.urls')),
    path('forum/', include('forum.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('course/', include('course.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Course, Lesson, Material


# Registering the Course model with import/export functionality
@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']
    list_filter = ['created_at']


# Registering the Lesson model with import/export functionality
@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin):
    list_display = ['title', 'course', 'created_at']
    search_fields = ['title', 'course__title']
    list_filter = ['created_at', 'course']


# Registering the Material model with import/export functionality
@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    list_display = ['material_type', 'lesson', 'created_at']
    search_fields = ['lesson__title', 'material_type']
    list_filter = ['material_type', 'created_at']

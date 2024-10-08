from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import StudentPerformance

# Define a resource class for the StudentPerformance model
class StudentPerformanceResource(resources.ModelResource):
    class Meta:
        model = StudentPerformance
        fields = ('performance_id', 'user_id__username', 'course_id__name', 'quiz_id', 'assignment_id', 'score', 'feedback')
        export_order = ('performance_id', 'user_id__username', 'course_id__name', 'quiz_id', 'assignment_id', 'score', 'feedback')

# Define an admin class that integrates with ImportExportModelAdmin
@admin.register(StudentPerformance)
class StudentPerformanceAdmin(ImportExportModelAdmin):
    resource_class = StudentPerformanceResource
    list_display = ('performance_id', 'user_id', 'course_id', 'quiz_id', 'assignment_id', 'score')
    search_fields = ('user_id__username', 'course_id__name')
    list_filter = ('course_id', 'score')
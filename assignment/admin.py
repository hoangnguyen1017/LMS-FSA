from django.contrib import admin
from .models import Assignment
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class AssignmentResource(resources.ModelResource):
    class Meta:
        model = Assignment
        fields = ('id', 'assignment_name', 'course', 'content', 'coding_exercises', 'created_at', 'created_by')  # Specify fields to export

@admin.register(Assignment)
class AssignmentAdmin(ImportExportModelAdmin):
    resource_class = AssignmentResource
    list_display = ('assignment_name', 'course', 'created_at', 'created_by')  # Displayed fields in the admin list view


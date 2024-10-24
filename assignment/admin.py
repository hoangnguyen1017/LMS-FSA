from django.contrib import admin
from .models import Assignment
from import_export.admin import ImportExportModelAdmin
from import_export import resources


class AssignmentResource(resources.ModelResource):
    class Meta:
        model = Assignment
        fields = (
            'id', 
            'assignment_name', 
            'course__course_name',  # Assuming 'name' is a field in the Course model
            'assignment_content', 
            'coding_exercises__title',  # Assuming 'title' is a field in the Exercise model
            'score', 
            'note', 
            'start_date', 
            'end_date'
        )
        export_order = (
            'id', 
            'assignment_name', 
            'course__name', 
            'assignment_content', 
            'coding_exercises__title', 
            'score', 
            'note', 
            'start_date', 
            'end_date'
        )


@admin.register(Assignment)
class AssignmentAdmin(ImportExportModelAdmin):
    resource_class = AssignmentResource
    list_display = ('assignment_name', 'course', 'start_date', 'end_date', 'score')
    search_fields = ('assignment_name', 'course__name')
    list_filter = ('course', 'start_date', 'end_date')

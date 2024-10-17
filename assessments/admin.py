# Register your models here.
from django.contrib import admin
from import_export import resources
from .models import Assessment
from import_export.admin import ImportExportModelAdmin


class AssessmentResource(resources.ModelResource):
    class Meta:
        model = Assessment
        fields = (
            'id',
            'title',
            'quiz__quiz_title',  # Assuming quiz has a title field
            'assignment__assignment_name',  # Assuming assignment has an assignment_name field
            'total_score',
            'created_at',
            'due_date',
            'created_by__username',  # Assuming the user model has a username field
        )
        export_order = (
            'id',
            'title',
            'quiz__quiz_title',
            'assignment__assignment_name',
            'total_score',
            'created_at',
            'due_date',
            'created_by__username',
        )


@admin.register(Assessment)
class AssessmentAdmin(ImportExportModelAdmin):
    resource_class = AssessmentResource
    list_display = ('title', 'quiz', 'assignment', 'total_score', 'created_by', 'due_date')
    search_fields = ('title', 'quiz__quiz_title', 'assignment__assignment_name', 'created_by__username')
    list_filter = ('due_date', 'created_at')


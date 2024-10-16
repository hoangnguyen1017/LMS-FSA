# Register your models here.
from django.contrib import admin
from import_export import resources
from .models import Assessment
from import_export.admin import ImportExportModelAdmin


# Registering Assessment model with Import/Export functionality
@admin.register(Assessment)
class AssessmentAdmin(ImportExportModelAdmin):
    list_display = ('title', 'due_date', 'created_at', 'created_by')
    search_fields = ('title', 'created_by__username')  # Add search functionality for created_by


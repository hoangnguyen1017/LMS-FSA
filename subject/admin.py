from django.contrib import admin

# Register your models here.
from .models import Subject

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Subject, Material

# Define resources for the models
class SubjectResource(resources.ModelResource):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'description', 'code')  # Specify fields you want to include in import/export

class MaterialResource(resources.ModelResource):
    class Meta:
        model = Material
        fields = ('id', 'subject__name', 'material_type', 'file', 'uploaded_at')  # Customize fields for import/export

# Register the Subject model with import/export functionality
@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    resource_class = SubjectResource
    list_display = ('name', 'code', 'description')  # Fields to display in admin list view
    search_fields = ('name', 'code')

# Register the Material model with import/export functionality
@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    resource_class = MaterialResource
    list_display = ('subject', 'material_type', 'file', 'uploaded_at')
    search_fields = ('subject__name', 'material_type')
    list_filter = ('subject', 'material_type')

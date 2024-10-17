
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Role

class RoleResource(resources.ModelResource):
    class Meta:
        model = Role
        # Optionally, specify fields to include or exclude
        fields = ('id', 'role_name',)  # Add or remove fields as necessary

@admin.register(Role)
class RoleAdmin(ImportExportModelAdmin):
    resource_class = RoleResource
    list_display = ('id', 'role_name',)  # Add more fields to display as needed
    search_fields = ('role_name',)  # Add search fields as needed

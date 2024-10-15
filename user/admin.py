from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .widgets import PasswordWidget

# Define UserResource for import/export handling
class UserResource(resources.ModelResource):
    password = fields.Field(
        column_name='password',
        attribute='password',
        widget=PasswordWidget()  
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'training_programs', 'modules')
        exclude = ('password',)  # Exclude password from export
        export_order = ('id', 'username', 'email', 'first_name', 'last_name', 'training_programs', 'modules')
    
    def dehydrate_password(self, user):
        return ""  # Return empty password for security reasons

# Custom User Admin with import/export
class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = UserResource
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    readonly_fields = ('date_joined',)

    # Adding training programs and modules fields to admin
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Training and Modules', {'fields': ('training_programs', 'modules')}),  # Added training programs and modules
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Define fields for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active', 'training_programs', 'modules')}
        ),
    )
    
    # Horizontal filter for ManyToMany relationships
    filter_horizontal = ('groups', 'user_permissions', 'training_programs', 'modules')  # Enable filtering for related fields
    
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

# Register the updated CustomUserAdmin
admin.site.register(User, CustomUserAdmin)

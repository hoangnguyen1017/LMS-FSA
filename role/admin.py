from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget
from .models import Role
from django.contrib.auth.models import Permission
from module_group.models import Module
from import_export import resources, fields
from import_export.results import RowResult

# Tạo resource cho model Role
class RoleResource(resources.ModelResource):
    permissions = fields.Field(
        column_name='permissions',
        attribute='permissions',
        widget=ManyToManyWidget(Permission, field='id')
    )
    modules = fields.Field(
        column_name='modules',
        attribute='modules',
        widget=ManyToManyWidget(Module, field='id')
    )

    class Meta:
        model = Role
        import_id_fields = ['role_name']  # Dùng role_name làm trường xác định duy nhất
        skip_unchanged = True
        report_skipped = True
        fields = ('role_name', 'permissions', 'modules')

    def before_import_row(self, row, **kwargs):
        role_name = row.get('role_name')
        if not role_name:
            return
        
        try:
            role = Role.objects.get(role_name=role_name)
            imported_permission_ids = set(int(id) for id in row.get('permissions', '').split(',') if id)
            imported_module_ids = set(int(id) for id in row.get('modules', '').split(',') if id)
            current_permission_ids = set(role.permissions.values_list('id', flat=True))
            current_module_ids = set(role.modules.values_list('id', flat=True))

            # Bỏ qua hàng nếu không có sự thay đổi
            if imported_permission_ids == current_permission_ids and imported_module_ids == current_module_ids:
                row[RowResult.IMPORT_TYPE_SKIP] = True
        except Role.DoesNotExist:
            pass

    def after_import_row(self, row, row_result, **kwargs):
        role_name = row.get('role_name')
        if not role_name:
            return
        role, created = Role.objects.get_or_create(role_name=role_name)

        permission_ids = [int(id) for id in row.get('permissions', '').split(',') if id]
        module_ids = [int(id) for id in row.get('modules', '').split(',') if id]

        if permission_ids:
            role.permissions.set(permission_ids)
        if module_ids:
            role.modules.set(module_ids)

    def export(self, queryset=None, *args, **kwargs):
        return super().export(queryset, *args, **kwargs)

# Cập nhật RoleAdmin để sử dụng ImportExportModelAdmin
class RoleAdmin(ImportExportModelAdmin):
    resource_class = RoleResource
    list_display = ('role_name', 'display_permissions', 'display_modules')
    search_fields = ('role_name',)
    filter_horizontal = ('permissions', 'modules')

    def display_permissions(self, obj):
        return ", ".join([str(permission.id) for permission in obj.permissions.all()])
    display_permissions.short_description = 'Permission IDs'

    def display_modules(self, obj):
        return ", ".join([str(module.id) for module in obj.modules.all()])
    display_modules.short_description = 'Module IDs'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "permissions":
            specific_permissions = Role._meta.permissions
            kwargs["queryset"] = Permission.objects.filter(
                codename__in=[codename for codename, _ in specific_permissions]
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

# Đăng ký mô hình Role với admin
admin.site.register(Role, RoleAdmin)
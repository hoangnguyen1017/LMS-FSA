from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Profile

# Tạo resource cho model User kết hợp với Profile
class UserProfileResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'profile__role__role_name',  # Lấy thông tin role từ Profile
            'profile__profile_picture_url',
            'profile__bio',
            'profile__interests',
            'profile__learning_style',
            'profile__preferred_language',
        )

# Tạo Inline cho Profile để thêm thông tin profile khi tạo User
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profile'

# Mở rộng UserAdmin mặc định để thêm chức năng nhập/xuất và quản lý Profile
class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = UserProfileResource
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_role')

    # Thêm ProfileInline để chỉnh sửa thông tin Profile ngay trong User form
    inlines = [ProfileInline]

    def get_role(self, obj):
        return obj.profile.role.role_name if hasattr(obj, 'profile') and obj.profile.role else 'No Role'
    get_role.short_description = 'Role'

# Đăng ký lại model User với lớp CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

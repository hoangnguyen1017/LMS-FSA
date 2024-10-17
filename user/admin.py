from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import User, Profile
from .forms import UserForm, UserEditForm
from .widgets import PasswordWidget

from .models import User, Profile  # Nhập User và Profile từ models
from import_export import resources
from import_export.admin import ImportExportModelAdmin

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
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    readonly_fields = ('date_joined',)

    # Fieldsets cho form quản lý người dùng
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Modules', {'fields': ('modules',)}),  # Thêm trường modules ở đây
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fieldsets cho việc thêm người dùng mới
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active', 'modules')}
        ),
    )
    filter_horizontal = ('groups', 'user_permissions', 'modules')

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    # Thêm ProfileInline để chỉnh sửa thông tin Profile ngay trong User form
    inlines = [ProfileInline]

    # Phương thức lấy role từ Profile
    def get_role(self, obj):
        return obj.profile.role.role_name if hasattr(obj, 'profile') and obj.profile.role else 'No Role'
    get_role.short_description = 'Role'

# Kiểm tra xem mô hình User có đã được đăng ký chưa
if User in admin.site._registry:
    admin.site.unregister(User)

# Đăng ký lại model User với lớp CustomUserAdmin
admin.site.register(User, CustomUserAdmin)



from import_export import resources
from .models import Student

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('id', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'enrolled_courses')
        export_order = ('id', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'enrolled_courses')
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profile'
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('user', 'enrolled_courses_display')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    inlines = [ProfileInline]

    def enrolled_courses_display(self, obj):
        return ", ".join(course.name for course in obj.enrolled_courses.all())
    enrolled_courses_display.short_description = 'Enrolled Courses'

# Đăng ký StudentAdmin với Student model
admin.site.register(Student, StudentAdmin)
admin.site.register(Profile)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import User, Profile, Role
from .forms import UserForm, UserEditForm
from .widgets import PasswordWidget
class UserProfileResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'profile__role__role_name',  # Profile Role
            'profile__bio',               # Profile Bio
            'profile__profile_picture_url',  # Profile Picture
            'profile__interests',          # Interests
            'profile__learning_style',     # Learning Style
            'profile__preferred_language', # Preferred Language
        )

    def before_import_row(self, row, **kwargs):
        # Lấy thông tin user từ file import
        username = row.get('username')
        email = row.get('email')
        first_name = row.get('first_name')
        last_name = row.get('last_name')

        # Tìm hoặc tạo mới User
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'first_name': first_name, 'last_name': last_name}
        )

        # Nếu user đã tồn tại, cập nhật các thông tin (email, first_name, last_name)
        if not created:
            user.email = email if email else user.email
            user.first_name = first_name if first_name else user.first_name
            user.last_name = last_name if last_name else user.last_name
            user.save()

        # Xử lý thông tin Profile liên kết với User
        profile, profile_created = Profile.objects.get_or_create(user=user)

        # Kiểm tra và gán Role nếu có trong file import
        role_name = row.get('profile__role__role_name')
        if role_name:
            role, role_created = Role.objects.get_or_create(role_name=role_name)
            profile.role = role
        
        # Cập nhật các thông tin khác cho Profile
        profile.bio = row.get('profile__bio') if row.get('profile__bio') else profile.bio
        profile.profile_picture_url = row.get('profile__profile_picture_url') if row.get('profile__profile_picture_url') else profile.profile_picture_url
        profile.interests = row.get('profile__interests') if row.get('profile__interests') else profile.interests
        profile.learning_style = row.get('profile__learning_style') if row.get('profile__learning_style') else profile.learning_style
        profile.preferred_language = row.get('profile__preferred_language') if row.get('profile__preferred_language') else profile.preferred_language
        
        # Lưu Profile sau khi cập nhật
        profile.save()

        # Gán ID cho row để tiếp tục quá trình import
        row['id'] = user.id

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Profile'

class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = UserProfileResource
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    readonly_fields = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Modules', {'fields': ('modules',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active', 'modules')}
        ),
    )
    filter_horizontal = ('groups', 'user_permissions', 'modules')

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    inlines = [ProfileInline]

    def get_role(self, obj):
        return obj.profile.role.role_name if hasattr(obj, 'profile') and obj.profile.role else 'No Role'
    get_role.short_description = 'Role'

if User in admin.site._registry:
    admin.site.unregister(User)

admin.site.register(User, CustomUserAdmin)

from import_export import resources
from .models import Student

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('id', 'student_code', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'enrolled_courses')
        export_order = ('id', 'student_code', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'enrolled_courses')

class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = ('student_code', 'user', 'enrolled_courses_display')
    search_fields = ('student_code', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    inlines = [ProfileInline]

    def enrolled_courses_display(self, obj):
        return ", ".join(course.course_name for course in obj.enrolled_courses.all())  
    enrolled_courses_display.short_description = 'Enrolled Courses'

admin.site.register(Student, StudentAdmin)
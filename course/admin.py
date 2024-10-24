from django.contrib import admin

# Register your models here.
from .models import Course, ReadingMaterial

from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Course  # Import the models
from user.models import User,UserCourseProgress 

# # Course Resource
# class CourseResource(resources.ModelResource):
#     created_by = fields.Field(
#         column_name='created_by__username',  # Assuming username is the desired attribute to import/export
#         attribute='created_by',
#         widget=ForeignKeyWidget(User, 'username')  # Use the username to link to the User model
#     )

#     class Meta:
#         model = Course
#         fields = ('id', 'course_name', 'course_description', 'created_by', 'created_at', 'updated_at')

# # UserCourseProgress Resource
# class UserCourseProgressResource(resources.ModelResource):
#     user = fields.Field(
#         column_name='user__username',  # Assuming username is the desired attribute to import/export
#         attribute='user',
#         widget=ForeignKeyWidget(User, 'username')  # Use the username to link to the User model
#     )
#     course = fields.Field(
#         column_name='course__course_name',  # Assuming course_name is the desired attribute to import/export
#         attribute='course',
#         widget=ForeignKeyWidget(Course, 'course_name')  # Use course_name to link to the Course model
#     )

#     class Meta:
#         model = UserCourseProgress
#         fields = ('id', 'user', 'course', 'progress_percentage', 'last_accessed')

# # Admin registration for Course
# @admin.register(Course)
# class CourseAdmin(ImportExportModelAdmin):
#     resource_class = CourseResource
#     list_display = ('course_name', 'created_by', 'created_at', 'updated_at')
#     search_fields = ('course_name', 'created_by__username')  # Searchable fields
#     list_filter = ('created_by',)  # Filter by created_by

# # Admin registration for UserCourseProgress
# @admin.register(UserCourseProgress)
# class UserCourseProgressAdmin(ImportExportModelAdmin):
#     resource_class = UserCourseProgressResource
#     list_display = ('user', 'course', 'progress_percentage', 'last_accessed')
#     search_fields = ('user__username', 'course__course_name')  # Searchable fields
#     list_filter = ('user', 'course')  # Filter by user and course

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Course, Session, Enrollment, ReadingMaterial, SessionCompletion

# Define resources for each model
class CourseResource(resources.ModelResource):
    class Meta:
        model = Course
        fields = ('id', 'course_name', 'course_code', 'description', 'creator', 'instructor', 'published', 'tags')  # Add fields you want to import/export

class SessionResource(resources.ModelResource):
    class Meta:
        model = Session
        fields = ('id', 'course__course_name', 'name', 'order')  # Customize as needed

class EnrollmentResource(resources.ModelResource):
    class Meta:
        model = Enrollment
        fields = ('id', 'student__username', 'course__course_name', 'date_enrolled')  # Customize as needed

class ReadingMaterialResource(resources.ModelResource):
    class Meta:
        model = ReadingMaterial
        fields = ('id', 'session__name', 'title', 'material_type', 'order')  # Customize as needed

class SessionCompletionResource(resources.ModelResource):
    class Meta:
        model = SessionCompletion
        fields = ('id', 'user__username', 'course__course_name', 'session__name', 'completed')  # Customize as needed

class UserCourseProgressResource(resources.ModelResource):
    class Meta:
        model = UserCourseProgress
        fields = ('id', 'user__username', 'course__course_name', 'progress_percentage', 'last_accessed')  # Customize as needed

# Register the Course model with import/export functionality
@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    resource_class = CourseResource
    list_display = ('course_name', 'course_code', 'creator', 'instructor', 'published')
    search_fields = ('course_name', 'course_code')

# Register the Session model with import/export functionality
@admin.register(Session)
class SessionAdmin(ImportExportModelAdmin):
    resource_class = SessionResource
    list_display = ('course', 'name', 'order')
    search_fields = ('course__course_name', 'name')

# Register the Enrollment model with import/export functionality
@admin.register(Enrollment)
class EnrollmentAdmin(ImportExportModelAdmin):
    resource_class = EnrollmentResource
    list_display = ('student', 'course', 'date_enrolled')
    search_fields = ('student__username', 'course__course_name')

# Register the ReadingMaterial model with import/export functionality
@admin.register(ReadingMaterial)
class ReadingMaterialAdmin(ImportExportModelAdmin):
    resource_class = ReadingMaterialResource
    list_display = ('session', 'title', 'order')
    search_fields = ('session__name', 'title')

# Register the SessionCompletion model with import/export functionality
@admin.register(SessionCompletion)
class SessionCompletionAdmin(ImportExportModelAdmin):
    resource_class = SessionCompletionResource
    list_display = ('user', 'course', 'session', 'completed')
    search_fields = ('user__username', 'course__course_name')

# Register the UserCourseProgress model with import/export functionality
@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(ImportExportModelAdmin):
    resource_class = UserCourseProgressResource
    list_display = ('user', 'course', 'progress_percentage', 'last_accessed')
    search_fields = ('user__username', 'course__course_name')


from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Subject, Category, Lesson, Material

# Define Resource classes for import/export functionality
class SubjectResource(resources.ModelResource):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'description', 'code')  # Define fields to be imported/exported


class CategoryResource(resources.ModelResource):
    subject = fields.Field(
        column_name='subject__name',  # This should match the column name in your import file
        attribute='subject',
        widget=ForeignKeyWidget(Subject, 'name')  # Use the 'name' field to match the subject
    )

    class Meta:
        model = Category
        fields = ('id', 'category_name', 'subject')  # Include 'subject' directly as it is a ForeignKey

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('category_name', 'subject')  # Ensure subject is displayed
    search_fields = ('category_name', 'subject__name')

class LessonResource(resources.ModelResource):
    subject = fields.Field(
        column_name='subject__name',
        attribute='subject',
        widget=ForeignKeyWidget(Subject, 'name')  # Match the subject by name
    )

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'subject__name', 'description', 'content', 'created_at')  # Added 'content'

@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin):
    resource_class = LessonResource
    list_display = ('title', 'subject', 'created_at', 'content')  # Added 'content'
    search_fields = ('title', 'subject__name', 'content')  # Added 'content' to search fields


class MaterialResource(resources.ModelResource):
    lesson = fields.Field(
        column_name='lesson__title',  # Use the lesson's title for import/export
        attribute='lesson',
        widget=ForeignKeyWidget(Lesson, 'title')  # Use 'title' for matching the lesson
    )

    class Meta:
        model = Material
        fields = ('id', 'lesson__subject__name', 'lesson__title', 'material_type', 'file', 'uploaded_at')

@admin.register(Material)
class MaterialAdmin(ImportExportModelAdmin):
    resource_class = MaterialResource
    list_display = ('lesson', 'material_type', 'uploaded_at')
    search_fields = ('lesson__title', 'material_type')
    list_filter = ('material_type', 'lesson__subject')

@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    resource_class = SubjectResource
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')

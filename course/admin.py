from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Course, Session
from django.contrib.auth.models import User


class CourseResource(resources.ModelResource):
    creator = fields.Field(
        attribute='creator',
        column_name='creator__username',
        widget=ForeignKeyWidget(User, 'username')
    )
    instructor = fields.Field(
        attribute='instructor',
        column_name='instructor__username',
        widget=ForeignKeyWidget(User, 'username')
    )
    prerequisites = fields.Field(
        attribute='prerequisites',
        column_name='prerequisites',
        widget=ManyToManyWidget(Course, field='course_name', separator='|')
    )

    class Meta:
        model = Course
        fields = (
            'course_name',
            'course_code',
            'description',
            'creator',
            'instructor',
            'published',
            'prerequisites',
        )
        import_id_fields = ('course_name',)

    def after_import(self, dataset, result, **kwargs):
        for row in dataset.dict:
            course_name = row['course_name']
            try:
                # Get the course by name
                course = Course.objects.get(course_name=course_name)

                # Process prerequisites after the course has been saved
                if row.get('prerequisites'):
                    prerequisites = row['prerequisites'].split('|')
                    for prereq_name in prerequisites:
                        prereq_name = prereq_name.strip()
                        if prereq_name:
                            # Find or create the prerequisite course using course_name
                            prereq_course, _ = Course.objects.get_or_create(course_name=prereq_name)
                            # Add the prerequisite to the course
                            course.prerequisites.add(prereq_course)
            except Course.DoesNotExist:
                print(f"Course '{course_name}' does not exist.")  # Handle missing courses

# Session resource class
class SessionResource(resources.ModelResource):
    course = fields.Field(attribute='course', column_name='course__course_name',
                           widget=ForeignKeyWidget(Course, 'course_name'))
    class Meta:
        model = Session
        fields = ('id', 'course', 'name', 'order')
        import_id_fields = ('id',)

@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    resource_class = CourseResource
    list_display = ('course_name', 'course_code', 'published')
    list_per_page = 5
    search_fields = ('course_name', 'course_code')
    list_filter = ('published',)

@admin.register(Session)
class SessionAdmin(ImportExportModelAdmin):
    resource_class = SessionResource
    list_display = ('course', 'name', 'order')
    search_fields = ('course__course_name', 'name')

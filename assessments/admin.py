# Register your models here.
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import AssessmentType, Assessment, StudentAssessmentAttempt

class AssessmentTypeResource(resources.ModelResource):
    class Meta:
        model = AssessmentType

class AssessmentResource(resources.ModelResource):
    class Meta:
        model = Assessment

class StudentAssessmentAttemptResource(resources.ModelResource):
    class Meta:
        model = StudentAssessmentAttempt


@admin.register(AssessmentType)
class AssessmentTypeAdmin(ImportExportModelAdmin):
    resource_class = AssessmentTypeResource
    list_display = ['type_name']

@admin.register(Assessment)
class AssessmentAdmin(ImportExportModelAdmin):
    resource_class = AssessmentResource
    list_display = ['title', 'course', 'assessment_type', 'due_date', 'total_score', 'created_by']

@admin.register(StudentAssessmentAttempt)
class StudentAssessmentAttemptAdmin(ImportExportModelAdmin):
    resource_class = StudentAssessmentAttemptResource
    list_display = ['user', 'assessment', 'score_quiz', 'score_ass', 'attempt_date']

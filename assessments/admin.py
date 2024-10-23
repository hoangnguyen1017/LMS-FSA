from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Assessment, InvitedCandidate, NonRegisteredCandidateAttempt, StudentAssessmentAttempt, UserAnswer, UserSubmission

# Define a resource for the Assessment model
class AssessmentResource(resources.ModelResource):
    class Meta:
        model = Assessment
        fields = ('id', 'course__course_name', 'title', 'assessment_type__type_name', 'invited_count', 'assessed_count', 'qualified_count', 'created_at', 'created_by__username')
        export_order = ('id', 'course__course_name', 'title', 'assessment_type__type_name', 'invited_count', 'assessed_count', 'qualified_count', 'created_at', 'created_by__username')

# Register Assessment with ImportExportModelAdmin
@admin.register(Assessment)
class AssessmentAdmin(ImportExportModelAdmin):
    resource_class = AssessmentResource
    list_display = ('title', 'course', 'assessment_type', 'invited_count', 'assessed_count', 'qualified_count')
    search_fields = ('title', 'course__name', 'assessment_type__type_name')
    list_filter = ('course', 'assessment_type')

# Define resources for other models and register similarly
class InvitedCandidateResource(resources.ModelResource):
    class Meta:
        model = InvitedCandidate

@admin.register(InvitedCandidate)
class InvitedCandidateAdmin(ImportExportModelAdmin):
    resource_class = InvitedCandidateResource
    list_display = ('email', 'assessment', 'invitation_date', 'expiration_date')
    search_fields = ('email', 'assessment__title')

class NonRegisteredCandidateAttemptResource(resources.ModelResource):
    class Meta:
        model = NonRegisteredCandidateAttempt

@admin.register(NonRegisteredCandidateAttempt)
class NonRegisteredCandidateAttemptAdmin(ImportExportModelAdmin):
    resource_class = NonRegisteredCandidateAttemptResource


class StudentAssessmentAttemptResource(resources.ModelResource):
    class Meta:
        model = StudentAssessmentAttempt
        fields = ('id', 'user__username', 'assessment__title', 'score_quiz', 'score_ass', 'attempt_date')

@admin.register(StudentAssessmentAttempt)
class StudentAssessmentAttemptAdmin(ImportExportModelAdmin):
    resource_class = StudentAssessmentAttemptResource
    list_display = ('user', 'assessment', 'score_quiz', 'score_ass', 'attempt_date')
    search_fields = ('user__username', 'assessment__title')
    list_filter = ('assessment', 'attempt_date')


from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import ProgrammingLanguage, Exercise, Submission
from import_export.widgets import ForeignKeyWidget
# Define resource for each model

class ProgrammingLanguageResource(resources.ModelResource):
    class Meta:
        model = ProgrammingLanguage
        fields = ('id', 'name')  # Specify fields to be exported/imported

# resources.py

class ExerciseResource(resources.ModelResource):
    language = fields.Field(
        column_name='language',
        attribute='language',
        widget=ForeignKeyWidget(ProgrammingLanguage, 'name')  # Use 'id' if you have IDs in the Excel file
    )

# Register models with ImportExportModelAdmin

@admin.register(ProgrammingLanguage)
class ProgrammingLanguageAdmin(ImportExportModelAdmin):
    resource_class = ProgrammingLanguageResource

@admin.register(Exercise)
class ExerciseAdmin(ImportExportModelAdmin):
    list_display = ('title', 'description', 'language')
    search_fields = ('title',)

@admin.register(Submission)
class SubmissionAdmin(ImportExportModelAdmin):
    list_display = ('exercise', 'student', 'created_at', 'score')
    search_fields = ('exercise__title', 'submission__student')
    list_filter = ('exercise',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('exercise', 'student')

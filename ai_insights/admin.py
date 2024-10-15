from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import AIInsights

class AI_InsightsResource(resources.ModelResource):
    class Meta:
        model = AIInsights
        fields = ('username','course','insight_text','insight_type','created_at',)  # Specify fields to include

@admin.register(AIInsights)
class AI_InsightsAdmin(ImportExportModelAdmin):
    resource_class = AI_InsightsResource

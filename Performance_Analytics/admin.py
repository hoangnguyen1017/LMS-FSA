from django.contrib import admin
from .models import PerformanceAnalytics
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class CertificateResource(resources.ModelResource):
    class Meta:
        model = PerformanceAnalytics
        exclude = ('id',)
        fields = ('analytics_id','average_score','completion_rate','predicted_performance','user_id','course_id')
        import_id_fields = ('certificate_id',)
class CertificateAdmin(ImportExportModelAdmin):
    resource_class = CertificateResource
    list_display = ('analytics_id','average_score','completion_rate','predicted_performance','user_id','course_id')

admin.site.register(PerformanceAnalytics, CertificateAdmin)



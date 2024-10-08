from django.contrib import admin
from .models import CourseCompletion
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class CertificateResource(resources.ModelResource):
    class Meta:
        model = CourseCompletion
        exclude = ('id',)
        fields = ('completion_id','user_id','course_id','course_id','completion_date')
        import_id_fields = ('certificate_id',)
class CertificateAdmin(ImportExportModelAdmin):
    resource_class = CertificateResource
    list_display = ('completion_id','user_id','course_id','course_id','completion_date')

admin.site.register(CourseCompletion, CertificateAdmin)


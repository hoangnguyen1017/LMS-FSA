from django.contrib import admin
from .models import Certificate
from import_export.admin import ImportExportModelAdmin
from import_export import resources


class CertificateResource(resources.ModelResource):
    class Meta:
        model = Certificate
        exclude = ('id',)
        fields = ('certificate_id','user_id','course_id','issue_date','certificate_url')
        import_id_fields = ('certificate_id',)
class CertificateAdmin(ImportExportModelAdmin):
    resource_class = CertificateResource
    list_display = ('certificate_id','user_id','course_id','issue_date','certificate_url')
admin.site.register(Certificate, CertificateAdmin)
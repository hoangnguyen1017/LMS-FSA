from import_export import resources
from .models import Certificate
from django.contrib import admin

class CertificateResource(resources.ModelResource):
    class Meta:
        model = Certificate
        fields = ('id', 'user__username', 'course__name', 'issue_date', 'certificate_url')  # Fields to include
        export_order = ('id', 'user__username', 'course__name', 'issue_date', 'certificate_url')  # Export order

admin.site.register(Certificate)
# from import_export.admin import ImportExportModelAdmin
# from django.contrib import admin
# from .models import Certificate

# @admin.register(Certificate)
# class CertificateAdmin(ImportExportModelAdmin):
#     resource_class = CertificateResource
#     list_display = ('user', 'course', 'issue_date', 'certificate_url')
#     search_fields = ('user__username', 'course__course_name')
#     list_filter = ('course', 'issue_date')

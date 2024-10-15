from django.contrib import admin
from .models import DiscussionThread  # Import your model
from .models import ThreadComments
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class DiscussionThreadResource(resources.ModelResource):
    class Meta:
        model = DiscussionThread

@admin.register(DiscussionThread)
class DiscussionThreadAdmin(ImportExportModelAdmin):
    resource_class = DiscussionThreadResource
    list_display = ('thread_title', 'created_by', 'created', 'updated')  # Customize as needed


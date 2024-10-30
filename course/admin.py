from django.contrib import admin

# Register your models here.
from .models import Course, ReadingMaterial

admin.site.register(Course)
admin.site.register(ReadingMaterial)

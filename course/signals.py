import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ReadingMaterial, CourseMaterial

@receiver(post_delete, sender=ReadingMaterial)
def auto_delete_reading_material_on_delete(sender, instance, **kwargs):
    # No file to delete, but remove the CourseMaterial entry
    CourseMaterial.objects.filter(material_id=instance.id, material_type='reading').delete()

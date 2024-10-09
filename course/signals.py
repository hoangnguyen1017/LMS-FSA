import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Document, Video, ReadingMaterial, CourseMaterial

@receiver(post_delete, sender=Document)
def auto_delete_document_on_delete(sender, instance, **kwargs):
    # Delete the associated file from the file system
    if instance.doc_file and os.path.isfile(instance.doc_file.path):
        os.remove(instance.doc_file.path)
    # Delete the corresponding CourseMaterial entry
    CourseMaterial.objects.filter(material_id=instance.id, material_type='document').delete()

@receiver(post_delete, sender=Video)
def auto_delete_video_on_delete(sender, instance, **kwargs):
    # Delete the associated file from the file system
    if instance.vid_file and os.path.isfile(instance.vid_file.path):
        os.remove(instance.vid_file.path)
    # Delete the corresponding CourseMaterial entry
    CourseMaterial.objects.filter(material_id=instance.id, material_type='video').delete()

@receiver(post_delete, sender=ReadingMaterial)
def auto_delete_reading_material_on_delete(sender, instance, **kwargs):
    # No file to delete, but remove the CourseMaterial entry
    CourseMaterial.objects.filter(material_id=instance.id, material_type='reading').delete()

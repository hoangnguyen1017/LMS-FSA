import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Document, Video, Subject

@receiver(post_delete, sender=Document)
def auto_delete_document_on_delete(sender, instance, **kwargs):
    if instance.doc_file and os.path.isfile(instance.doc_file.path):
        os.remove(instance.doc_file.path)

@receiver(post_delete, sender=Video)
def auto_delete_video_on_delete(sender, instance, **kwargs):
    if instance.vid_file and os.path.isfile(instance.vid_file.path):
        os.remove(instance.vid_file.path)

@receiver(post_delete, sender=Subject)
def auto_delete_subject_files(sender, instance, **kwargs):
    # Delete associated documents
    for document in Document.objects.filter(subject=instance):
        if document.doc_file and os.path.isfile(document.doc_file.path):
            os.remove(document.doc_file.path)

    # Delete associated videos
    for video in Video.objects.filter(subject=instance):
        if video.vid_file and os.path.isfile(video.vid_file.path):
            os.remove(video.vid_file.path)

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import  Certificate
# from course.models import UserCourseProgress

# @receiver(post_save, sender=UserCourseProgress)
# def create_certificate(sender, instance, created, **kwargs):
#     if instance.progress_percentage == 100:
#         Certificate.objects.update_or_create(user=instance.user, course=instance.course)

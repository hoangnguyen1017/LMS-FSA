from django.db import models
from user.models import User
from course.models import Course
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from quiz.models import StudentQuizAttempt

class ProgressNotification(models.Model):    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    notification_message = models.CharField(max_length=255, blank=True, null=True)
    notification_date = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=StudentQuizAttempt)
def create_progress_notification(sender, instance, created, **kwargs):
    if created:
        # Tạo nội dung thông báo
        message = f"You finished {instance.quiz.quiz_title} with a score of {instance.score}."
        
        # Tạo bản ghi mới trong ProgressNotification
        ProgressNotification.objects.create(
            user=instance.user,
            course=instance.quiz.course,  # Nếu quiz liên kết với course
            notification_message=message
        )

@receiver(post_delete, sender=StudentQuizAttempt)
def delete_progress_notification(sender, instance, **kwargs):
    # Xóa tất cả các thông báo liên quan đến StudentQuizAttempt bị xóa
    ProgressNotification.objects.filter(user=instance.user, course=instance.quiz.course).delete()
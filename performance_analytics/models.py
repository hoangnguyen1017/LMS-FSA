from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.apps import apps
from course.models import Course
from user.models import User


class PerformanceAnalytics(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    average_score = models.FloatField(default=0.0)
    completion_rate = models.IntegerField(default=0.0)

    # def update_performance(self):
    #     # Dynamically import models using get_model
    #     StudentQuizAttempt = apps.get_model('quiz', 'StudentQuizAttempt')
    #     Quiz = apps.get_model('quiz', 'Quiz')

    #     completed_quizzes = StudentQuizAttempt.objects.filter(user=self.user.id, quiz__course=self.course)
    #     total_quizzes = Quiz.objects.filter(course=self.course).count()
        
    #     if total_quizzes > 0:
    #         total_score = completed_quizzes.aggregate(models.Sum('score'))['score__sum'] or 0
    #         self.average_score = round(total_score / total_quizzes, 1)
    #         completed_quizzes_count = completed_quizzes.filter(score__gt=0).count()
    #         self.completion_rate = round(completed_quizzes_count / total_quizzes, 2) * 100
    #     else:
    #         self.average_score = 0.0
    #         self.completion_rate = 0.0
        
    #     self.save()

    class Meta:
        db_table = 'performance'


# @receiver(post_save, sender='quiz.StudentQuizAttempt')
# def update_performance_analytics(sender, instance, **kwargs):
#     # Use apps.get_model for dynamic imports to avoid circular imports
#     PerformanceAnalytics = apps.get_model('performance_analytics', 'PerformanceAnalytics')

#     try:
#         performance = PerformanceAnalytics.objects.get(user=instance.user, course=instance.quiz.course)
#     except PerformanceAnalytics.DoesNotExist:
#         performance = PerformanceAnalytics(user=instance.user, course=instance.quiz.course)
    
#     performance.update_performance()


# @receiver(post_save, sender='quiz.Quiz')
# def update_completion_rate(sender, instance, created, **kwargs):
#     # Use apps.get_model for dynamic imports to avoid circular imports
#     PerformanceAnalytics = apps.get_model('performance_analytics', 'PerformanceAnalytics')

#     try:
#         performance = PerformanceAnalytics.objects.get(course=instance.course)
#     except PerformanceAnalytics.DoesNotExist:
#         performance = PerformanceAnalytics(course=instance.course)
    
#     performance.update_performance()

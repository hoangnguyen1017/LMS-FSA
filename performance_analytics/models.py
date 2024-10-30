from django.db import models
from course.models import Course,Enrollment
from assessments.models import Assessment, StudentAssessmentAttempt
from user.models import User,Student
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from django.db.models import OuterRef, Subquery,Max
from django.contrib.auth.decorators import login_required
# Create your models here.
class PerformanceAnalytics(models.Model):
    id = models.AutoField(primary_key=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    average_score = models.FloatField(default=0.0)
    completion_rate = models.FloatField(default=0.0)

    def update_performance(self):
        highest_score = StudentAssessmentAttempt.objects.filter(
            user=self.user, assessment=OuterRef('assessment')
        ).values('assessment').annotate(highest_score=Max('score_ass')).values('highest_score')

        highest_attempts = StudentAssessmentAttempt.objects.filter(
            user=self.user,
            assessment__course=self.course,
            score_ass__in=Subquery(highest_score)
        )
        
        total_assessments = Assessment.objects.filter(course=self.course).count()
        if total_assessments > 0:
            completed_assessments = highest_attempts.filter().count()
            print('count:',completed_assessments)
            total_score = highest_attempts.aggregate(models.Sum('score_ass'))['score_ass__sum'] or 0
            self.average_score = round(total_score / completed_assessments, 3)
            self.completion_rate = round((completed_assessments / total_assessments) * 100, 2)
        else:
            self.average_score = 0.0
            self.completion_rate = 0.0
        self.save()
    
    class Meta:
        db_table = 'performance' 

@receiver(post_save, sender=StudentAssessmentAttempt)
@receiver(post_delete, sender=StudentAssessmentAttempt)
def update_performance_analytics(sender, instance, **kwargs):
    try:
        performance = PerformanceAnalytics.objects.get(
            user=instance.user,
            course=instance.assessment.course 
        )
        performance.update_performance()
    except PerformanceAnalytics.DoesNotExist:
        pass



@receiver(post_save, sender=Assessment)
@receiver(post_delete, sender=Assessment)
def update_performance_analytics(sender, instance, **kwargs):
        students = User.objects.filter(id__in=StudentAssessmentAttempt.objects.filter(assessment__course=instance.course).values('user'))
        for student in students:
            performance = PerformanceAnalytics.objects.get(
                user=student,
                course=instance.course
            )
        performance.update_performance()


@receiver(post_save, sender=Enrollment)
def create_performance(sender, instance, created, **kwargs):
    if created:
        PerformanceAnalytics.objects.create(
            user=instance.student,
            course=instance.course
        )

@receiver(post_delete, sender=Enrollment)
def delete_performance(sender, instance, **kwargs):
    try:
        performance = PerformanceAnalytics.objects.get(
            user=instance.student,
            course=instance.course
        )
        performance.delete()
    except PerformanceAnalytics.DoesNotExist:
        pass
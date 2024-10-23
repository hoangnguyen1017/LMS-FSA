from django.db import models
from course.models import Course
from course.models import UserCourseProgress

# # Create your models here.
# class UserCourseProgress(models.Model):
#     user = models.ForeignKey('user.User', on_delete=models.CASCADE)  # String reference to avoid circular import
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
#     last_accessed = models.DateTimeField(auto_now=True)  # Updated to reflect last accessed time

#     class Meta:
#         unique_together = ('user', 'course')

#     def __str__(self):
#         return f"{self.user} - {self.course} - {self.progress_percentage}%"
    

from django.db import models
from training_program_for_courses.models import TrainingProgramCourse
from course.models import Course

class TrainingProgramCourses(models.Model):
    program = models.ForeignKey(TrainingProgramCourse, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.IntegerField(choices=[(i, f'Semester {i}') for i in range(1, 10)], default=1)

    class Meta:
        unique_together = ('program', 'course', 'semester')

    def __str__(self):
        return f"{self.program} - {self.course} - Semester {self.semester}"


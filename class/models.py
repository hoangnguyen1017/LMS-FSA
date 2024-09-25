from django.db import models

# Create your models here.
class ClassInfo(models.Model):
    id_class = models.CharField(max_length=255,unique=True)
    number_student = models.PositiveIntegerField()
    class_mentor= models.CharField(max_length=255)
    def __str__(self):
        return f"{self.id_class} - {self.class_mentor}"
    

from django.db import models

class Student(models.Model):
    class_info = models.ForeignKey(ClassInfo, related_name='students', on_delete=models.CASCADE)
    student_id = models.CharField(max_length=255, unique=True)  # Thêm trường student_id
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=511, editable=False)  # Không cần người dùng nhập

    def save(self, *args, **kwargs):
        self.full_name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)
        

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"  # Hiển thị student_id cùng với full_name

    

    
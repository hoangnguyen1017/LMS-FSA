from django.db import models
from ckeditor.fields import RichTextField

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content = RichTextField()  # Rich text editor for composing lectures
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Material(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    file = models.FileField(upload_to='materials/')
    material_type = models.CharField(max_length=50, choices=[('assignment', 'Assignment'), ('lab', 'Lab'), ('lecture', 'Lecture')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.material_type} - {self.file.name}"

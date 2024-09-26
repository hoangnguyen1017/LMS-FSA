from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_subjects')
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_subjects')

    def __str__(self):
        return self.name

class Prerequisite(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_prerequisites')
    prerequisite_subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='prerequisite_for_subjects')

    class Meta:
        unique_together = ('subject', 'prerequisite_subject')

    def __str__(self):
        return f"{self.prerequisite_subject.name} is a prerequisite for {self.subject.name}"

# Mô hình lưu trữ tài liệu
class Document(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='documents')
    doc_title = models.CharField(max_length=255)
    doc_file = models.FileField(upload_to='documents/', blank=True, null=True)

    def __str__(self):
        return self.doc_title


# Mô hình lưu trữ video
class Video(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='videos')
    vid_title = models.CharField(max_length=255)
    vid_file = models.FileField(upload_to='videos/', blank=True, null=True)

    def __str__(self):
        return self.vid_title


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student} enrolled in {self.subject}"
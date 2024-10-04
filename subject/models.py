from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_subjects')
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_subjects')
    published = models.BooleanField(default=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='is_prerequisite_for')

    def __str__(self):
        return self.name

    def get_completion_percent(self):
        all_materials = SubjectMaterial.objects.filter(subject=self)
        total_materials = all_materials.count()
        completed_materials = Completion.objects.filter(
            subject=self,
            completed=True
        ).count()

        if total_materials > 0:
            return (completed_materials / total_materials) * 100
        return 0

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



class ReadingMaterial(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='reading_materials')
    content = RichTextUploadingField()  # Use RichTextUploadingField for HTML content with file upload capability
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class SubjectMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('document', 'Document'),
        ('video', 'Video'),
        ('reading', 'Reading Material'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='materials')
    material_id = models.PositiveIntegerField()
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPE_CHOICES)
    order = models.PositiveIntegerField()  # Order of appearance
    title = models.CharField(max_length=255)

    def __str__(self):
        return 'subject id: ' +  str(self.subject.id ) + '   title: ' + str(self.title)

    class Meta:
        ordering = ['order']

class Completion(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    reading = models.ForeignKey(ReadingMaterial, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('subject', 'document', 'video', 'reading')

    def __str__(self):
        return f"Completion for {'document' if self.document else 'video'} in {self.subject}"

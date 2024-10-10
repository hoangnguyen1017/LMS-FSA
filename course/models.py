from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


class Course(models.Model):
    name = models.CharField(max_length=255, unique=True)
    course_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_courses')
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_courses')
    published = models.BooleanField(default=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='is_prerequisite_for')
    tags = models.TextField(blank=True)  # mới thêm

    def __str__(self):
        return self.name

    def get_completion_percent(self, user):
        total_sessions = self.sessions.count()
        completed_sessions = SessionCompletion.objects.filter(session__course=self, user=user, completed=True).count()
        return (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0


class Session(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions', null=True)
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField()  # Order of appearance

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class ReadingMaterial(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='materials', null=True)
    content = RichTextUploadingField()  # Use RichTextUploadingField for HTML content with file upload capability
    title = models.CharField(max_length=255)
    material_type = models.CharField(max_length=50, default='reading', editable=False)  # Add material_type as a database field
    order = models.PositiveIntegerField()  # Order of appearance

    def save(self, *args, **kwargs):
        self.material_type = 'reading'  # Automatically set the material type before saving
        super().save(*args, **kwargs)  # Call the parent class's save method

    def __str__(self):
        return f'session id: {self.session.id}   title: {self.title}'

    class Meta:
        ordering = ['order']


class Completion(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(ReadingMaterial, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'material', 'user')

    def __str__(self):
        return f"Completion for {self.material} in {self.session}"


class SessionCompletion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('course', 'user', 'session')  # Ensures a user can only complete a session once

    def __str__(self):
        return f"{self.user} completed session: {self.session.name}"


def mark_session_complete(course, user, session):
    # Count the total materials in the session
    total_materials = session.materials.count()

    # Count completed materials by checking the Completion model
    completed_materials = Completion.objects.filter(session=session, user=user, completed=True).count()

    # Check if all materials are completed
    if total_materials == completed_materials:
        # Mark the session as complete in the SessionCompletion model
        SessionCompletion.objects.update_or_create(
            user=user,
            session=session,
            defaults={'completed': True}
        )

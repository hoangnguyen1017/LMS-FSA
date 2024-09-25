from django.db import models
from subject.models import Subject

#Create your models here.
class Study(models.Model):
    study_subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    study_link = models.URLField()
    image = models.ImageField(upload_to="study_images/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.study_subject.name} Study'
    



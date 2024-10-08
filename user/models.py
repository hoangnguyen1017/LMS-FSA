from django.db import models

from django.contrib.auth.models import User
from role.models import Role

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    profile_picture_url = models.URLField(max_length=10000, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)  # Thêm trường bio
    interests = models.TextField(blank=True, null=True)  # Thêm trường interests
    learning_style = models.CharField(max_length=50, blank=True, null=True)  # Thêm trường learning_style
    preferred_language = models.CharField(max_length=50, blank=True, null=True)  # Thêm trường preferred_language
    last_login = models.DateTimeField(blank=True, null=True)  # Thêm trường last_login


    
    def __str__(self):
        return f"{self.user.username} - {self.role.role_name if self.role else 'No Role'}"


from django.db import models


class Registration(models.Model):
    username = models.CharField(max_length=100)

    full_name = models.CharField(max_length=255, blank=True, default='')

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True, default='')

    # Đặt related_name cho groups và user_permissions để tránh xung đột
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Thay đổi tên để không bị xung đột
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Thay đổi tên để không bị xung đột
        blank=True,
    )

    def __str__(self):
        return self.username




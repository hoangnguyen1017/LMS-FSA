# Generated by Django 5.1.1 on 2024-10-31 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0002_remove_member_email_remove_member_profile_picture_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='email',
            field=models.EmailField(default=1, max_length=254, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='member',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profiles/'),
        ),
        migrations.AddField(
            model_name='member',
            name='role',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]

# Generated by Django 5.0.9 on 2024-11-12 08:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collaboration_group', '0005_feedback'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='groups',
        ),
        migrations.AddField(
            model_name='feedback',
            name='groups',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='collaboration_group.collaborationgroup'),
            preserve_default=False,
        ),
    ]

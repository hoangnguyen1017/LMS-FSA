# Generated by Django 5.1.1 on 2024-11-05 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0010_alter_member_role_delete_teammaterial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='role',
            field=models.CharField(choices=[('Leader', 'Leader'), ('Manager', 'Manager'), ('Member', 'Member')], max_length=10),
        ),
    ]

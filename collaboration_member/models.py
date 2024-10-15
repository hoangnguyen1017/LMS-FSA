from django.db import models
from collaboration_group.models import CollaborationGroup  # Import your CollaborationGroup model
from user.models import User  # Import your User model

from django.db import models

class GroupMember(models.Model):
    member_id = models.IntegerField(primary_key=True)
    group = models.ForeignKey(CollaborationGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.member_id:
            # Calculate the next member_id for this group
            max_id = GroupMember.objects.filter(group=self.group).aggregate(models.Max('member_id'))['member_id__max']
            self.member_id = 1 if max_id is None else max_id + 1
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.user.username} in {self.group.group_name}"


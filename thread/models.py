from django.db import models
from django.utils import timezone
from subject.models import Subject  # Assuming the subject app is named 'subject'
from user.models import User        # Assuming the user app is named 'user'

class DiscussionThread(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL,null= True,blank= True)  # created_by
    thread_title = models.CharField(max_length=255)
    thread_content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)  # Ensure this field exists
    updated = models.DateTimeField(auto_now=True)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE,null=True,blank= True)
    
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.thread_title
    class Meta:
        ordering = ['-updated']
    
    
class ThreadComments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name='comments')  # Reference to the discussion thread
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference to the user who made the comment
    comment_text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)  # Automatically set on comment creation
    updated = models.DateTimeField(auto_now=True)  # Automatically updated when the comment is updated

    def __str__(self):
        return f"Comment by {self.user.username} on {self.thread.thread_title}"

    class Meta:
        ordering = ['-created']
    

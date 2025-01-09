from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Submission(models.Model):
    task = models.ForeignKey(Task, related_name='submissions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='submissions', on_delete=models.CASCADE)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)



    def save(self, *args, **kwargs):
        # If the submission is not approved, do not set completed_at
        if not self.is_approved:
            self.completed_at = None  
        elif self.is_approved and not self.completed_at:
            self.completed_at = models.DateTimeField(auto_now_add=True) 
            
        super().save(*args, **kwargs)  # Call the parent class's save method

    def __str__(self):
        return f'Submission by {self.user} for task {self.task}'

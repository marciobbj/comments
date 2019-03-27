from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.

User = get_user_model()


class Comment(models.Model):
    content = models.TextField(blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes_comments = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(blank=True, null=True)

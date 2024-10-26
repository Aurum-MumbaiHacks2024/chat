from django.db import models
from core.models import *

class Chat(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=True)
    title = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    context = models.TextField()
    class Meta:
        ordering = ['-id']

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=20)
    content = models.TextField()
    content_html = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['timestamp']
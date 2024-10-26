from django.db import models
from core.models import *
from .llm import llm_response
import threading

class IPO(models.Model):
    ipo_name = models.CharField(max_length=40, unique=True, primary_key=True)
    issue_size = models.IntegerField()
    issue_price = models.IntegerField()
    qib = models.FloatField()
    hni = models.FloatField()
    rii = models.FloatField()
    age = models.IntegerField()
    predicted_opening = models.IntegerField(blank=True)

class Chat(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=True)
    title = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    context = models.ManyToManyField(IPO, blank=True, related_name="chats")
    class Meta:
        ordering = ['-id']

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=20)
    content = models.TextField()
    content_html = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    context = models.ManyToManyField(IPO, blank=True, related_name="messages")
    class Meta:
        ordering = ['timestamp']
# Generated by Django 5.1.2 on 2024-10-26 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_remove_message_context_remove_chat_context_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='context',
        ),
        migrations.AddField(
            model_name='chat',
            name='context',
            field=models.TextField(default='m'),
            preserve_default=False,
        ),
    ]

from django.db import models

# Create your models here.

class Chat(models.Model):
    keyword = models.CharField(
        max_length=255,
        help_text="可用,分隔", 
        default=""
    )
        
    response = models.CharField(max_length=255)

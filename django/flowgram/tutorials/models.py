from django.db import models

class Tutorial(models.Model):
    position = models.FloatField(default=0.0)
    title = models.CharField(max_length=2048)
    content = models.TextField(blank=True)
    active = models.BooleanField(default=False)
    video_path = models.CharField(max_length=100)


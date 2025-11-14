from django.db import models
from django.contrib.auth.models import User

class Video(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('downloading', 'Downloading'),
        ('downloaded', 'Downloaded'),
        ('failed', 'Failed'),
    ]
    MEDIA_TYPE_CHOICES = [
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    title = models.CharField(max_length=255)
    youtube_url = models.URLField()
    local_path = models.CharField(max_length=255, blank=True, null=True)
    thumbnail_path = models.CharField(max_length=255, blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='video')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'title']]

    def __str__(self):
        return self.title

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    videos = models.ManyToManyField(Video, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

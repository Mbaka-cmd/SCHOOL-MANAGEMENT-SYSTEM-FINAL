from django.db import models
from django.utils import timezone
from schools.models import School


class Notice(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'Everyone'),
        ('students', 'Students Only'),
        ('parents', 'Parents Only'),
        ('staff', 'Staff Only'),
    ]
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('important', 'Important'),
        ('urgent', 'Urgent'),
    ]
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notices')
    title = models.CharField(max_length=200)
    content = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    is_active = models.BooleanField(default=True)
    posted_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now().date() > self.expires_at
        return False

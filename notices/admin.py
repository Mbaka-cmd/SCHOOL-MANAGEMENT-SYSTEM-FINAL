from django.contrib import admin
from .models import Notice

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'audience', 'priority', 'is_active', 'posted_by', 'created_at']
    list_filter = ['audience', 'priority', 'is_active']

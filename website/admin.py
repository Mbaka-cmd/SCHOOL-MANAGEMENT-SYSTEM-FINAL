from django.contrib import admin
from .models import CoCurricularActivity, GalleryAlbum, GalleryPhoto, KCSEResult, NewsEvent

@admin.register(CoCurricularActivity)
class CoCurricularActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_published', 'order']
    list_filter = ['category', 'is_published']
    list_editable = ['is_published', 'order']
    search_fields = ['name']

@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'event_date']
    list_filter = ['category', 'is_published']

@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ['album', 'caption', 'order']

@admin.register(KCSEResult)
class KCSEResultAdmin(admin.ModelAdmin):
    list_display = ['year', 'mean_grade', 'mean_points', 'is_published']
    list_filter = ['is_published']

@admin.register(NewsEvent)
class NewsEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'post_type', 'is_published', 'created_at']
    list_filter = ['post_type', 'is_published']

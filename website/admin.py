from django.contrib import admin
from .models import KCSEResult, NewsEvent, GalleryAlbum, GalleryPhoto, ParentComment, CoCurricularActivity


@admin.register(KCSEResult)
class KCSEResultAdmin(admin.ModelAdmin):
    list_display = ['school', 'year', 'mean_grade', 'candidates_sat', 'university_qualifiers', 'pass_rate', 'is_published']
    list_filter = ['school', 'is_published', 'year']
    list_editable = ['is_published']
    ordering = ['-year']
    search_fields = ['school__name', 'year', 'mean_grade']


@admin.register(NewsEvent)
class NewsEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'post_type', 'school', 'is_published', 'is_featured', 'created_at']
    list_filter = ['school', 'post_type', 'is_published', 'is_featured']
    list_editable = ['is_published', 'is_featured']
    search_fields = ['title', 'content']
    ordering = ['-created_at']


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'school', 'is_published', 'created_at']
    list_filter = ['school', 'is_published']
    list_editable = ['is_published']
    search_fields = ['title', 'description']
    ordering = ['-created_at']


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ['album', 'caption', 'is_featured', 'created_at']
    list_filter = ['album', 'is_featured']
    list_editable = ['is_featured']
    search_fields = ['caption']
    ordering = ['-created_at']


@admin.register(ParentComment)
class ParentCommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'school', 'rating', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['school', 'is_approved', 'is_featured', 'rating']
    list_editable = ['is_approved', 'is_featured']
    search_fields = ['author_name', 'comment']
    ordering = ['-created_at']


@admin.register(CoCurricularActivity)
class CoCurricularActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'category', 'is_active']
    list_filter = ['school', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name', 'category', 'description']
from django.contrib import admin
from .models import Artwork, Comment, LikeRecord


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'ai_type', 'user', 'likes', 'views', 'is_public', 'created_at']
    list_filter = ['ai_type', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'prompt']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['artwork', 'user', 'content', 'created_at']


@admin.register(LikeRecord)
class LikeRecordAdmin(admin.ModelAdmin):
    list_display = ['artwork', 'user', 'created_at']

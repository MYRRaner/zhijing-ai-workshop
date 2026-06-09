from django.contrib import admin
from .models import CreativeProject


@admin.register(CreativeProject)
class CreativeProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'project_type', 'user', 'is_public', 'created_at']
    list_filter = ['project_type', 'is_public', 'created_at']
    search_fields = ['title', 'description']

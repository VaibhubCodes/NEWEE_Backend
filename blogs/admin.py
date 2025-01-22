from django.contrib import admin
from .models import Blog, Comment, Tag, SavedBlog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'subject', 'view_count', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('subject', 'created_at', 'tags')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'content', 'created_at')
    search_fields = ('content',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(SavedBlog)
class SavedBlogAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'saved_at')

from django.contrib import admin
from .models import Ebook

@admin.register(Ebook)
class EbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'chapter', 'topic', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('subject', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('title', 'description', 'pdf_file', 'cover_image', 'subject', 'chapter', 'topic')

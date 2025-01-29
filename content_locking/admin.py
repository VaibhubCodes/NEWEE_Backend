from django.contrib import admin
from .models import PurchasedContent

@admin.register(PurchasedContent)
class PurchasedContentAdmin(admin.ModelAdmin):
    list_display = ("user", "content_type", "content_id", "purchase_date")
    list_filter = ("content_type",)
    search_fields = ("user__email", "content_type")

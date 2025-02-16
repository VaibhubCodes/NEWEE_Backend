from django.contrib import admin
from .models import SupportTicket

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_id", "subject", "student", "assigned_controller", "category", "priority", "status", "created_at")
    list_filter = ("priority", "status", "created_at")
    search_fields = ("ticket_id", "subject", "student__name", "assigned_controller__name")
    readonly_fields = ("ticket_id", "created_at", "updated_at", "comments")

    fieldsets = (
        ("Ticket Information", {"fields": ("ticket_id", "student", "assigned_controller", "category", "subject", "description")}),
        ("Status & Priority", {"fields": ("priority", "status")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
        ("Comments", {"fields": ("comments",)}),
    )

    def save_model(self, request, obj, form, change):
        """Override save to ensure assigned controller is not a student."""
        if obj.assigned_controller and obj.assigned_controller.role == "Student":
            raise ValueError("A student cannot be assigned as a controller.")
        super().save_model(request, obj, form, change)

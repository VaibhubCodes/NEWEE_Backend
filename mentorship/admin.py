from django.contrib import admin
from .models import MentorAvailability, MentorshipSession, MentorshipSettings, Question


@admin.register(MentorshipSettings)
class MentorshipSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing mentorship settings (XamCoins costs).
    """
    list_display = ('cost_per_question', 'max_cost_30_minutes', 'max_cost_60_minutes')
    list_display_links = None  # No fields will act as a link
    list_editable = ('cost_per_question', 'max_cost_30_minutes', 'max_cost_60_minutes')  # All fields in `list_display` are editable



@admin.register(MentorAvailability)
class MentorAvailabilityAdmin(admin.ModelAdmin):
    """
    Admin configuration for mentor availability and booked slots.
    """
    list_display = ('teacher', 'start_time', 'end_time', 'is_booked')
    list_filter = ('is_booked', 'teacher')
    search_fields = ('teacher__email',)
    readonly_fields = ('is_booked',)  # Prevent manual edits to booking status


@admin.register(MentorshipSession)
class MentorshipSessionAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing mentorship sessions.
    """
    list_display = ('student', 'teacher', 'start_time', 'duration_minutes', 'cost', 'is_confirmed')
    list_filter = ('is_confirmed', 'teacher')
    search_fields = ('student__email', 'teacher__email')
    readonly_fields = ('cost', 'start_time', 'duration_minutes')  # Ensure historical data remains consistent


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing student questions.
    """
    list_display = ('student', 'subject', 'content', 'created_at', 'answered')
    list_filter = ('answered', 'subject')
    search_fields = ('student__email', 'subject__name', 'content')
    readonly_fields = ('created_at',)  # Ensure timestamps are not editable

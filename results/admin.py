from django.contrib import admin
from .models import Participant, Answer, Leaderboard

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'rank', 'correct_answers', 'completed_at', 'result_status')
    list_filter = ('quiz', 'result_status')
    search_fields = ('user__username', 'quiz__title')
    actions = ['toggle_result_visibility']

    def toggle_result_visibility(self, request, queryset):
        for participant in queryset:
            participant.result_status = not participant.result_status
            participant.save()
    toggle_result_visibility.short_description = "Toggle Result Visibility"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('participant', 'section_question', 'selected_option', 'is_correct', 'marks_obtained')
    search_fields = ('participant__user__username',)


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'generated_at')
    search_fields = ('quiz__title',)

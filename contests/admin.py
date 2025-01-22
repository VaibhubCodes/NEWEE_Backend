from django.contrib import admin
from .models import Contest, Participant, PrizeDistribution

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ['title', 'quiz', 'entry_fee', 'participant_limit', 'winner_percentage', 'start_time', 'end_time']
    search_fields = ['title', 'quiz__title']
    list_filter = ['start_time', 'end_time']

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'contest', 'rank', 'prize', 'joined_at']
    search_fields = ['user__username', 'contest__title']
    list_filter = ['joined_at']

@admin.register(PrizeDistribution)
class PrizeDistributionAdmin(admin.ModelAdmin):
    list_display = ['contest', 'rank', 'prize_amount']
    search_fields = ['contest__title']
    list_filter = ['rank']

from django.contrib import admin
from .models import XamCoinSettings, BlogReadingActivity, ContestStreak, ContestStreakReward, LockedXamCoins

@admin.register(XamCoinSettings)
class XamCoinSettingsAdmin(admin.ModelAdmin):
    list_display = ('time_threshold', 'coins_per_minute')
    ordering = ('time_threshold',)

@admin.register(BlogReadingActivity)
class BlogReadingActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'total_time_spent', 'coins_earned', 'is_idle')
    list_filter = ('is_idle',)
    readonly_fields = ('start_time', 'last_active_time')

@admin.register(ContestStreak)
class ContestStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'streak_count', 'last_participation_date', 'total_xamcoins_collected')
    search_fields = ('user__email',)
    list_filter = ('last_participation_date',)


@admin.register(ContestStreakReward)
class ContestStreakRewardAdmin(admin.ModelAdmin):
    list_display = ('day', 'reward_amount', 'bonus_percentage')
    list_editable = ('reward_amount', 'bonus_percentage')
    ordering = ('day',)


@admin.register(LockedXamCoins)
class LockedXamCoinsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_locked', 'last_settlement_day')
    search_fields = ('user__email',)
from rest_framework import serializers
from .models import BlogReadingActivity, XamCoinSettings, ContestStreak, ContestStreakReward

class XamCoinSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = XamCoinSettings
        fields = ['time_threshold', 'coins_per_minute']

class BlogReadingActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogReadingActivity
        fields = [
            'id', 'user', 'blog', 'start_time', 'last_active_time',
            'is_idle', 'total_time_spent', 'coins_earned'
        ]

class ContestStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestStreak
        fields = ["streak_count", "last_participation_date", "bonus_earned"]


class ContestStreakRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestStreakReward
        fields = ["day", "reward_amount"]
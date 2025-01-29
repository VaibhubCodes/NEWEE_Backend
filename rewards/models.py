from django.db import models
from django.contrib.auth import get_user_model
from blogs.models import Blog

User = get_user_model()

class XamCoinSettings(models.Model):
    time_threshold = models.IntegerField(help_text="Time threshold in minutes")
    coins_per_minute = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="XamCoins credited per minute after this threshold"
    )

    def __str__(self):
        return f"{self.time_threshold} mins: {self.coins_per_minute} coins/minute"

class BlogReadingActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_activities")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="activities")
    start_time = models.DateTimeField(auto_now_add=True)
    last_active_time = models.DateTimeField(auto_now=True)
    is_idle = models.BooleanField(default=False)
    total_time_spent = models.PositiveIntegerField(default=0, help_text="Total time spent in seconds")
    coins_earned = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0, 
        help_text="Total XamCoins earned"
    )

    def __str__(self):
        return f"{self.user} on {self.blog.title}"

class ContestStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="contest_streak")
    streak_count = models.PositiveIntegerField(default=0, help_text="Current streak count in days")
    last_participation_date = models.DateField(null=True, blank=True, help_text="Date of last contest participation")
    total_xamcoins_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total XamCoins collected during the streak")

    def reset_streak(self):
        self.streak_count = 0
        self.last_participation_date = None
        self.total_xamcoins_collected = 0.00
        self.save()

    def __str__(self):
        return f"{self.user.email} - Streak: {self.streak_count}, Collected: {self.total_xamcoins_collected}"


class ContestStreakReward(models.Model):
    day = models.PositiveIntegerField(unique=True, help_text="Day of the streak")
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, help_text="XamCoins rewarded for this day in the streak")
    bonus_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Bonus percentage for settlement on this day")

    class Meta:
        ordering = ['day']

    def __str__(self):
        return f"Day {self.day} → Reward: {self.reward_amount} XamCoins, Bonus: {self.bonus_percentage}%"


class LockedXamCoins(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="locked_xamcoins")
    total_locked = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total locked XamCoins from the streak")
    last_settlement_day = models.PositiveIntegerField(null=True, blank=True, help_text="Last settlement day reached")

    def __str__(self):
        return f"{self.user.email} → Locked: {self.total_locked} XamCoins"
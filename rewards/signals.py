from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from contests.models import Participant
from .models import ContestStreak, ContestStreakReward, LockedXamCoins
from wallets.models import Wallet, Transaction
from datetime import  timedelta
@receiver(post_save, sender=Participant)
def update_contest_streak(sender, instance, created, **kwargs):
    """
    Update the contest streak and lock XamCoins during the streak.
    """
    if created:
        user = instance.user
        today = now().date()

        # Get or create streak record
        streak, _ = ContestStreak.objects.get_or_create(user=user)

        # Check if participation is consecutive
        if streak.last_participation_date == today - timedelta(days=1):
            streak.streak_count += 1  # Increment streak
        elif streak.last_participation_date != today:
            streak.streak_count = 1  # Reset streak if missed a day

        # Update streak data
        streak.last_participation_date = today

        # Fetch or create locked XamCoins record
        locked_coins, _ = LockedXamCoins.objects.get_or_create(user=user)

        # Fetch daily reward for the current streak day
        reward = ContestStreakReward.objects.filter(day=streak.streak_count).first()
        daily_xamcoins = reward.reward_amount if reward else 0

        # Lock XamCoins
        streak.total_xamcoins_collected += daily_xamcoins
        locked_coins.total_locked += daily_xamcoins
        streak.save()
        locked_coins.save()

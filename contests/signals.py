from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Contest, PrizeDistribution, Participant
from quizzes.models import Quiz
from decimal import Decimal

@receiver(post_save, sender=Contest)
def create_prize_distribution(sender, instance, created, **kwargs):
    """
    Automatically generate prize distribution when a contest is created.
    """
    if created:
        total_pool = instance.entry_fee * instance.participant_limit
        prize_pool = total_pool * (1 - (instance.admin_commission / 100))
        num_winners = round(instance.participant_limit * (instance.winner_percentage / 100))

        # Generate rank weights
        weights = [1 / (i ** 0.5) for i in range(1, num_winners + 1)]
        total_weight = sum(weights)

        # Calculate prizes for each rank
        for rank, weight in enumerate(weights, start=1):
            prize_amount = round((prize_pool * (weight / total_weight)), 2)
            PrizeDistribution.objects.create(contest=instance, rank=rank, prize_amount=prize_amount)


@receiver(pre_delete, sender=Participant)
def enforce_participation_limits(sender, instance, **kwargs):
    """
    Ensure participants cannot join more than 3 contests with the same quiz.
    """
    contest = instance.contest
    user = instance.user

    # Check if the user is in more than 3 contests for the same quiz
    contests_with_same_quiz = Participant.objects.filter(
        user=user, contest__quiz=contest.quiz
    ).count()

    if contests_with_same_quiz > 3:
        raise ValueError("A user cannot participate in more than 3 contests for the same quiz.")

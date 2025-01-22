from django.db import models
from django.conf import settings
from quizzes.models import Quiz

class Contest(models.Model):
    quiz = models.OneToOneField(
        Quiz, on_delete=models.CASCADE, related_name="contest", help_text="Quiz associated with this contest",null=True
    )
    title = models.CharField(max_length=255, help_text="Title of the contest")
    description = models.TextField(blank=True, help_text="Short description of the contest")
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, help_text="Entry fee for the contest")
    participant_limit = models.PositiveIntegerField(help_text="Maximum number of participants allowed",default=1)
    winner_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage of winners",default=62)
    admin_commission = models.DecimalField(max_digits=5, decimal_places=2, default=15.0, help_text="Admin commission in percentage")
    start_time = models.DateTimeField(help_text="Start time of the contest")
    end_time = models.DateTimeField(help_text="End time of the contest")

    def __str__(self):
        return self.title

class Participant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contest_participations"
    )
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name="participants", help_text="Contest this participant joined"
    )
    rank = models.PositiveIntegerField(null=True, blank=True, help_text="Rank of the participant")
    prize = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Prize amount won")
    joined_at = models.DateTimeField(auto_now_add=True, help_text="Time when the user joined")

    def __str__(self):
        return f"{self.user.username} in {self.contest.title}"

class PrizeDistribution(models.Model):
    contest = models.ForeignKey(
        Contest, on_delete=models.CASCADE, related_name="prizes", help_text="Contest associated with the prizes"
    )
    rank = models.PositiveIntegerField(help_text="Rank in the contest")
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prize amount for this rank")

    def __str__(self):
        return f"Contest: {self.contest.title} - Rank {self.rank} Prize {self.prize_amount}"

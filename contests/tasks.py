from celery import shared_task
from django.utils.timezone import now
from .models import Contest, Participant
from results.models import Participant as QuizParticipant
from wallets.models import Wallet
from datetime import timedelta
@shared_task
def auto_end_contests():
    """
    Automatically end contests whose end time has passed.
    """
    contests = Contest.objects.filter(end_time__lt=now())
    for contest in contests:
        quiz_participants = QuizParticipant.objects.filter(quiz=contest.quiz).order_by("rank")
        prize_distribution = contest.prizes.order_by("rank")

        for prize in prize_distribution:
            if prize.rank <= len(quiz_participants):
                quiz_participant = quiz_participants[prize.rank - 1]
                participant = Participant.objects.get(contest=contest, user=quiz_participant.user)
                participant.prize = prize.prize_amount
                participant.save()

                # Credit prize to winnings wallet
                winnings_wallet, _ = Wallet.objects.get_or_create(user=quiz_participant.user, wallet_type="winnings")
                winnings_wallet.balance += prize.prize_amount
                winnings_wallet.save()

        contest.delete()  # Clean up the contest after processing

@shared_task
def clear_old_contest_data():
    """
    Periodically clean up old contests and their associated data.
    """
    expired_contests = Contest.objects.filter(end_time__lt=now() - timedelta(days=30))
    for contest in expired_contests:
        contest.prizes.all().delete()
        contest.participants.all().delete()
        contest.delete()

from celery import shared_task
from django.utils.timezone import now
from results.models import Participant
from quizzes.models import Quiz

@shared_task
def auto_submit_quizzes():
    """
    Task to automatically submit incomplete quizzes once the end time is passed.
    """
    quizzes = Quiz.objects.filter(end_date__lt=now(), is_active=True)
    for quiz in quizzes:
        participants = Participant.objects.filter(quiz=quiz, completed_at__isnull=True)
        for participant in participants:
            participant.auto_submit_quiz()


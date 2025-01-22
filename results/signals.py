from django.db.models.signals import post_save
from django.dispatch import receiver
from threading import local
from results.models import Participant, Leaderboard

# Define thread-local storage
_local = local()

def ensure_signal_running_initialized():
    if not hasattr(_local, 'signal_running'):
        _local.signal_running = False


@receiver(post_save, sender=Participant)
def update_ranks_on_submission(sender, instance, **kwargs):
    ensure_signal_running_initialized()  # Ensure the attribute is initialized

    # Avoid recursive or redundant signal calls
    if _local.signal_running:
        return

    try:
        _local.signal_running = True

        if kwargs.get('update_fields') and 'completed_at' not in kwargs['update_fields']:
            return  # Skip rank update if not finalizing

        leaderboard, _ = Leaderboard.objects.get_or_create(quiz=instance.quiz)
        leaderboard.calculate_leaderboard()

    finally:
        _local.signal_running = False  # Reset the signal_running flag

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PayoutRequest
from wallets.models import Wallet
from decimal import Decimal

@receiver(post_save, sender=PayoutRequest)
def handle_payout_status_change(sender, instance, **kwargs):
    """
    Signal to handle updates to the payout request's status.
    If the payout is rejected, refund the amount to the user's wallet.
    """
    # Ensure we act only on updates
    if kwargs.get("created", False):
        return

    if instance.status == "rejected":
        wallet = instance.wallet
        wallet.balance += Decimal(instance.amount)  # Refund the amount
        wallet.save()
        print(f"Refunded ₹{instance.amount} to wallet {wallet.id} due to payout rejection.")

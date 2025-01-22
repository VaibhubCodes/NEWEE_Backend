from django.db.models.signals import post_save
from django.dispatch import receiver
from wallets.models import Wallet, Referral, ReferralBonus
from users.models import CustomUser
from django.db import models

@receiver(post_save, sender=CustomUser)
def create_user_wallets(sender, instance, created, **kwargs):
    if created:
        # Create all wallets including XamCoins
        Wallet.objects.get_or_create(user=instance, wallet_type='earnexam')
        Wallet.objects.get_or_create(user=instance, wallet_type='winnings')
        Wallet.objects.get_or_create(user=instance, wallet_type='discount')
        Wallet.objects.get_or_create(user=instance, wallet_type='xamcoins')


        # Handle referral logic
        if hasattr(instance, 'referral_code') and instance.referral_code:
            try:
                referrer = CustomUser.objects.get(referral_code=instance.referral_code)

                # Create a referral record
                Referral.objects.create(referrer=referrer, referred=instance)

                # Fetch referral bonus amounts
                referral_bonus = ReferralBonus.objects.first()
                if referral_bonus:
                    # Update wallets with bonus amounts
                    Wallet.objects.filter(user=referrer, wallet_type='earnexam').update(
                        balance=models.F('balance') + referral_bonus.referrer_amount
                    )
                    Wallet.objects.filter(user=instance, wallet_type='earnexam').update(
                        balance=models.F('balance') + referral_bonus.referral_amount
                    )
            except CustomUser.DoesNotExist:
                pass  # Invalid referral code, skip referral bonus

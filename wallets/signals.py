from django.db.models.signals import post_save
from django.dispatch import receiver
from wallets.models import Wallet, Referral, ReferralBonus
from users.models import CustomUser
from django.db import models

@receiver(post_save, sender=CustomUser)
def create_user_wallets(sender, instance, created, **kwargs):
    if created:
        # Create wallets for new users
        Wallet.objects.get_or_create(user=instance, wallet_type='earnexam')
        Wallet.objects.get_or_create(user=instance, wallet_type='winnings')
        Wallet.objects.get_or_create(user=instance, wallet_type='discount')
        Wallet.objects.get_or_create(user=instance, wallet_type='xamcoins')

        # Handle referral logic
        if hasattr(instance, 'referral_code') and instance.referral_code:
            try:
                referrer = CustomUser.objects.get(referral_code=instance.referral_code)

                # Create referral record
                Referral.objects.create(referrer=referrer, referred=instance)

                # Fetch initial referral bonus
                referral_bonus = ReferralBonus.objects.first()
                if referral_bonus:
                    # Credit initial referral bonus to referred user
                    referred_wallet = Wallet.objects.get(user=instance, wallet_type='earnexam')
                    referred_wallet.credit(referral_bonus.referred_user_bonus)

                    # Credit initial referral bonus to referrer
                    referrer_wallet = Wallet.objects.get(user=referrer, wallet_type='earnexam')
                    referrer_wallet.credit(referral_bonus.referrer_amount)

                # Count total referrals for referrer
                total_referrals = Referral.objects.filter(referrer=referrer).count()

                # Fetch applicable milestone bonus (Only Referrer gets it)
                milestone_bonus = ReferralBonus.objects.filter(milestone=total_referrals).first()

                if milestone_bonus:
                    # Update referrer's wallet with milestone bonuses
                    Wallet.objects.filter(user=referrer, wallet_type='earnexam').update(
                        balance=models.F('balance') + milestone_bonus.referrer_amount
                    )

            except CustomUser.DoesNotExist:
                pass  # Invalid referral code, skip referral bonus

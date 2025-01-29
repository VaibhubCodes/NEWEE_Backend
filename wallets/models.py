from django.db import models
from django.conf import settings
from users.models import CustomUser
class Wallet(models.Model):
    WALLET_TYPES = [
        ('earnexam', 'Earnexam Wallet'),
        ('winnings', 'Winnings Wallet'),
        ('discount', 'Discount Bonus Wallet'),
        ('xamcoins', 'XamCoins'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallets'
    )
    wallet_type = models.CharField(max_length=10, choices=WALLET_TYPES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('user', 'wallet_type')

    def __str__(self):
        return f"{self.user.email} - {self.get_wallet_type_display()}"

    def credit(self, amount):
        self.balance += amount
        self.save()

    def debit(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

class XamCoinConversion(models.Model):
    conversion_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Conversion rate (e.g., 1 XamCoin = INR value)"
    )
    conversion_commission = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.00,
        help_text="Commission percentage for conversion"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Only one rule can be active at a time"
    )

    class Meta:
        verbose_name = "XamCoin Conversion Rule"
        verbose_name_plural = "XamCoin Conversion Rules"

    def __str__(self):
        return f"Rate: {self.conversion_rate}, Commission: {self.conversion_commission}%"
    
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name='transactions'
    )
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user.email} - {self.transaction_type} - {self.amount}"

class Referral(models.Model):
    referrer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referrals')
    referred = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='referral')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.email} referred {self.referred.email}"


class ReferralBonus(models.Model):
    milestone = models.IntegerField(default=1, help_text="Number of referrals required for this bonus")
    referrer_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100.00, help_text="Bonus for referrer when reaching milestone")
    referred_user_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, help_text="One-time bonus for referred user on signup")

    def __str__(self):
        return f"{self.milestone} Referrals → Referrer Bonus: {self.referrer_amount}, Referred User Bonus: {self.referred_user_bonus}"
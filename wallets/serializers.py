from rest_framework import serializers
from .models import Wallet, Transaction, XamCoinConversion
from users.models import CustomUser
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'wallet_type', 'balance']


class TransactionSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer()

    class Meta:
        model = Transaction
        fields = ['id', 'wallet', 'transaction_type', 'amount', 'description', 'timestamp']

class ReferralCodeSerializer(serializers.Serializer):
    referral_code = serializers.CharField()

    def validate_referral_code(self, value):
        if not CustomUser.objects.filter(referral_code=value).exists():
            raise serializers.ValidationError("Invalid referral code.")
        return value
    
class XamCoinConversionSerializer(serializers.ModelSerializer):
    class Meta:
        model = XamCoinConversion
        fields = ['conversion_rate', 'commission_percentage']
from rest_framework import serializers
from .models import Payment, PayoutRequest
from decimal import Decimal

class AddFundsSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        error_messages={
            "required": "Amount is required.",
            "invalid": "Enter a valid decimal amount."
        }
    )

    def validate_amount(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class PaymentSerializer(serializers.Serializer):
    razorpay_payment_id = serializers.CharField(
        required=True, error_messages={"required": "Razorpay payment ID is required."}
    )
    razorpay_order_id = serializers.CharField(
        required=True, error_messages={"required": "Razorpay order ID is required."}
    )
    razorpay_signature = serializers.CharField(
        required=True, error_messages={"required": "Razorpay signature is required."}
    )
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=True,
        error_messages={
            "required": "Amount is required.",
            "invalid": "Enter a valid amount."
        }
    )


class PayoutRequestSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=True,
        error_messages={
            "required": "Amount is required.",
            "invalid": "Enter a valid amount."
        }
    )

    class Meta:
        model = PayoutRequest
        fields = ['id', 'user', 'wallet', 'amount', 'status', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

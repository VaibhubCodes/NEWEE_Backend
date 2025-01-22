from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, Transaction,Referral,ReferralBonus, XamCoinConversion
from .serializers import WalletSerializer, TransactionSerializer,ReferralCodeSerializer,XamCoinConversionSerializer
from users.models import CustomUser
from django.db.models import F
from decimal import Decimal

class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet_types = ['earnexam', 'winnings', 'discount']
        for wallet_type in wallet_types:
            Wallet.objects.get_or_create(user=request.user, wallet_type=wallet_type)

        wallets = Wallet.objects.filter(user=request.user)
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data)



class CreditWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet_type = request.data.get('wallet_type')
        amount = request.data.get('amount')

        try:
            wallet = Wallet.objects.get(user=request.user, wallet_type=wallet_type)
            wallet.credit(float(amount))
            Transaction.objects.create(
                wallet=wallet, transaction_type='credit', amount=amount, description='Wallet credit'
            )
            return Response({"message": f"{amount} credited to {wallet.get_wallet_type_display()} successfully."})
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found."}, status=404)


class DebitWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet_type = request.data.get('wallet_type')
        amount = request.data.get('amount')

        try:
            wallet = Wallet.objects.get(user=request.user, wallet_type=wallet_type)
            if wallet.debit(float(amount)):
                Transaction.objects.create(
                    wallet=wallet, transaction_type='debit', amount=amount, description='Wallet debit'
                )
                return Response({"message": f"{amount} debited from {wallet.get_wallet_type_display()} successfully."})
            else:
                return Response({"error": "Insufficient balance."}, status=400)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found."}, status=404)


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(wallet__user=request.user).order_by('-timestamp')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class ApplyReferralCodeView(APIView):
    def post(self, request):
        serializer = ReferralCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        referral_code = serializer.validated_data['referral_code']
        try:
            referrer = CustomUser.objects.get(referral_code=referral_code)
            referred_user = request.user

            if Referral.objects.filter(referred=referred_user).exists():
                return Response({"error": "Referral already applied."}, status=status.HTTP_400_BAD_REQUEST)

            # Create referral record
            Referral.objects.create(referrer=referrer, referred=referred_user)

            # Fetch referral bonus amounts
            referral_bonus = ReferralBonus.objects.first()
            if referral_bonus:
                # Update wallets with bonus amounts
                referrer_wallet = Wallet.objects.get(user=referrer, wallet_type='earnexam')
                referred_wallet = Wallet.objects.get(user=referred_user, wallet_type='earnexam')

                referrer_wallet.balance += referral_bonus.referrer_amount
                referred_wallet.balance += referral_bonus.referral_amount

                referrer_wallet.save()
                referred_wallet.save()

                # Create transactions for referral bonuses
                Transaction.objects.create(
                    wallet=referrer_wallet,
                    transaction_type='credit',
                    amount=referral_bonus.referrer_amount,
                    description=f"Referral bonus for referring {referred_user.email}"
                )
                Transaction.objects.create(
                    wallet=referred_wallet,
                    transaction_type='credit',
                    amount=referral_bonus.referral_amount,
                    description=f"Referral bonus for being referred by {referrer.email}"
                )

            return Response({"success": "Referral applied successfully."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid referral code."}, status=status.HTTP_400_BAD_REQUEST)



class XamCoinPurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = Decimal(request.data.get("amount", 0))
        wallet = Wallet.objects.get(user=request.user, wallet_type='earnexam')

        if wallet.balance < amount:
            return Response({"error": "Insufficient balance in Earnexam Wallet."}, status=400)

        # Deduct from Earnexam Wallet and credit to XamCoins
        wallet.debit(amount)
        xamcoins_wallet, _ = Wallet.objects.get_or_create(user=request.user, wallet_type='xamcoins')
        xamcoins_wallet.credit(amount)

        # Record transactions
        Transaction.objects.create(wallet=wallet, transaction_type='debit', amount=amount, description="Purchase XamCoins")
        Transaction.objects.create(wallet=xamcoins_wallet, transaction_type='credit', amount=amount, description="Purchased XamCoins")

        return Response({"message": "XamCoins purchased successfully!"}, status=200)


class XamCoinToMoneyConversionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        xamcoins_to_convert = Decimal(request.data.get("xamcoins", 0))
        xamcoins_wallet = Wallet.objects.get(user=request.user, wallet_type='xamcoins')

        if xamcoins_wallet.balance < xamcoins_to_convert:
            return Response({"error": "Insufficient XamCoins balance."}, status=400)

        # Fetch conversion details
        conversion_details = XamCoinConversion.objects.first()
        if not conversion_details:
            return Response({"error": "XamCoin conversion details not found."}, status=500)

        conversion_rate = conversion_details.conversion_rate
        commission_percentage = conversion_details.commission_percentage

        # Calculate money after commission
        total_amount = xamcoins_to_convert * conversion_rate
        commission = total_amount * (commission_percentage / 100)
        final_amount = total_amount - commission

        # Deduct XamCoins and credit to Winnings Wallet
        xamcoins_wallet.debit(xamcoins_to_convert)
        winnings_wallet, _ = Wallet.objects.get_or_create(user=request.user, wallet_type='winnings')
        winnings_wallet.credit(final_amount)

        # Record transactions
        Transaction.objects.create(wallet=xamcoins_wallet, transaction_type='debit', amount=xamcoins_to_convert, description="Converted XamCoins to money")
        Transaction.objects.create(wallet=winnings_wallet, transaction_type='credit', amount=final_amount, description="XamCoin conversion credit")

        return Response({"message": "XamCoins converted successfully!", "amount_credited": final_amount}, status=200)


class XamCoinConversionDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversion_details = XamCoinConversion.objects.first()
        if not conversion_details:
            return Response({"error": "Conversion details not found."}, status=500)

        serializer = XamCoinConversionSerializer(conversion_details)
        return Response(serializer.data, status=200)
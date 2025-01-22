from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from wallets.models import Wallet
from .models import Payment, PayoutRequest
from .serializers import PaymentSerializer, PayoutRequestSerializer, AddFundsSerializer
import razorpay
from django.db import transaction
from decimal import Decimal
from django.conf import settings

# Initialize Razorpay client
RAZORPAY_API_KEY = settings.RAZORPAY_API_KEY
RAZORPAY_API_SECRET = settings.RAZORPAY_API_SECRET
razorpay_client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))

class AddFundsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddFundsSerializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Ensure the amount is properly formatted and multiplied for Razorpay
            amount = int(serializer.validated_data['amount'] * 100)

            print(f"Creating Razorpay order for amount (in paise): {amount}")

            # Create Razorpay order
            razorpay_order = razorpay_client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            })

            return Response({
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': RAZORPAY_API_KEY,
                'amount': serializer.validated_data['amount']
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Unexpected error during Razorpay order creation: {str(e)}")
            return Response({'error': f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payment_id = serializer.validated_data['razorpay_payment_id']
        order_id = serializer.validated_data['razorpay_order_id']
        signature = serializer.validated_data['razorpay_signature']
        amount = serializer.validated_data['amount']

        try:
            # Verify Razorpay payment signature
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            # Check if payment already exists to avoid duplicates
            payment, created = Payment.objects.get_or_create(
                payment_id=payment_id,
                defaults={
                    'user': request.user,
                    'wallet': Wallet.objects.get(user=request.user, wallet_type='earnexam'),
                    'amount': amount,
                    'status': 'completed'
                }
            )

            if not created:  # Payment already processed
                return Response({"error": "Payment already verified and processed."}, status=status.HTTP_400_BAD_REQUEST)

            # Credit the 'earnexam' wallet
            wallet = Wallet.objects.get(user=request.user, wallet_type='earnexam')
            wallet.credit(Decimal(amount))

            return Response({"status": "Payment verified and wallet updated"}, status=status.HTTP_200_OK)

        except Wallet.DoesNotExist:
            return Response({"error": "Earnexam Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')

        try:
            wallet = Wallet.objects.get(user=request.user, wallet_type='earnexam')
            # Create Razorpay order
            razorpay_order = razorpay_client.order.create({
                "amount": int(float(amount) * 100),  # Amount in paisa
                "currency": "INR",
                "payment_capture": "1",
            })

            payment = Payment.objects.create(
                user=request.user,
                wallet=wallet,
                amount=amount,
                payment_id=razorpay_order['id'],
                status='pending'
            )
            return Response({"order_id": razorpay_order['id'], "amount": amount})
        except Wallet.DoesNotExist:
            return Response({"error": "Earnexam Wallet not found."}, status=404)


class ConfirmPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')

        try:
            payment = Payment.objects.get(payment_id=payment_id)

            # Verify payment
            razorpay_client.payment.capture(razorpay_payment_id, int(payment.amount * 100))

            payment.status = 'completed'
            payment.save()

            # Credit wallet
            payment.wallet.credit(payment.amount)

            return Response({"message": "Payment confirmed successfully."})
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=404)
        except razorpay.errors.BadRequestError:
            payment.status = 'failed'
            payment.save()
            return Response({"error": "Payment verification failed."}, status=400)


class RequestPayoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")

        # Validate the amount
        try:
            amount = Decimal(amount)  # Convert amount to Decimal
            if amount <= 0:
                return Response(
                    {"error": "Invalid amount. Must be greater than zero."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid amount format. Must be a number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # Check if winnings wallet exists
                wallet = Wallet.objects.get(user=request.user, wallet_type="winnings")

                # Check if wallet has enough balance
                if wallet.balance < amount:
                    return Response(
                        {"error": "Insufficient balance."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Deduct amount from wallet immediately
                wallet.balance -= amount  # Perform subtraction with Decimal
                wallet.save()

                # Create the payout request
                payout_request = PayoutRequest.objects.create(
                    user=request.user,
                    wallet=wallet,
                    amount=amount,
                    status="pending",
                )

                return Response(
                    {
                        "message": "Payout request submitted successfully.",
                        "payout_id": payout_request.id,
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Wallet.DoesNotExist:
            return Response(
                {"error": "Winnings Wallet not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            # Log the exception
            print(f"Error in RequestPayoutView: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class ApprovePayoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, payout_id):
        try:
            payout_request = PayoutRequest.objects.get(id=payout_id)

            if payout_request.status != "pending":
                return Response({"error": "Payout request is not in pending state."}, status=400)

            # Approve the payout
            payout_request.status = "approved"
            payout_request.save()

            return Response(
                {"message": "Payout approved successfully."},
                status=status.HTTP_200_OK,
            )
        except PayoutRequest.DoesNotExist:
            return Response(
                {"error": "Payout request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RejectPayoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, payout_id):
        try:
            payout_request = PayoutRequest.objects.get(id=payout_id)

            if payout_request.status != "pending":
                return Response(
                    {"error": "Payout request is not in a pending state."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update the payout status to rejected
            payout_request.status = "rejected"
            payout_request.save()

            return Response(
                {"message": "Payout rejected successfully, and amount will be refunded."},
                status=status.HTTP_200_OK,
            )
        except PayoutRequest.DoesNotExist:
            return Response(
                {"error": "Payout request not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"Error in RejectPayoutView: {str(e)}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


        
class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wallets = Wallet.objects.filter(user=request.user)
            wallet_data = {
                'earnexam': wallets.filter(wallet_type='earnexam').first().balance if wallets.filter(wallet_type='earnexam').exists() else 0.0,
                'winnings': wallets.filter(wallet_type='winnings').first().balance if wallets.filter(wallet_type='winnings').exists() else 0.0,
                'discount': wallets.filter(wallet_type='discount').first().balance if wallets.filter(wallet_type='discount').exists() else 0.0,
            }
            return Response(wallet_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PayoutListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all payout requests for the logged-in user
            payouts = PayoutRequest.objects.filter(user=request.user).order_by("-created_at")
            serializer = PayoutRequestSerializer(payouts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ebooks.models import Ebook
from blogs.models import Blog
from StudyMaterial.models import StudyMaterial
from .models import PurchasedContent
from wallets.models import Wallet, Transaction
from decimal import Decimal
from .serializers import PurchasedContentSerializer

class PurchasedContentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        purchased_items = PurchasedContent.objects.filter(user=request.user)
        serializer = PurchasedContentSerializer(purchased_items, many=True)
        return Response(serializer.data)

class UnlockContentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content_type = request.data.get("content_type")  # e.g., "ebook", "blog", "study_material"
        content_id = request.data.get("content_id")  # ID of the content to unlock
        wallet_type = request.data.get("wallet_type", "xamcoins")  # Default to XamCoins

        try:
            # Fetch the content
            if content_type == "ebook":
                content = Ebook.objects.get(id=content_id)
            elif content_type == "blog":
                content = Blog.objects.get(id=content_id)
            elif content_type == "study_material":
                content = StudyMaterial.objects.get(id=content_id)
            else:
                return Response({"error": "Invalid content type."}, status=400)

            # Check if the content is premium
            if not content.is_premium:
                return Response({"error": "This content is not premium and does not require unlocking."}, status=400)

            # Check if the user already unlocked this content
            if PurchasedContent.objects.filter(user=request.user, content_type=content_type, content_id=content.id).exists():
                return Response({"message": "Content already unlocked!"}, status=200)

            # Get unlock cost
            unlock_cost = content.unlock_cost

            # Check user's wallet balance
            wallet = Wallet.objects.get(user=request.user, wallet_type=wallet_type)
            if wallet.balance < unlock_cost:
                return Response({"error": "Insufficient funds to unlock content."}, status=400)

            # Deduct the cost from the user's wallet
            wallet.balance -= Decimal(unlock_cost)
            wallet.save()

            # Record the transaction
            Transaction.objects.create(
                wallet=wallet,
                transaction_type="debit",
                amount=unlock_cost,
                description=f"Unlocked premium {content_type} ID: {content.id}"
            )

            # Mark the content as purchased
            PurchasedContent.objects.create(
                user=request.user,
                content_type=content_type,
                content_id=content.id
            )

            return Response({"message": f"{content_type.capitalize()} unlocked successfully!"}, status=200)

        except (Ebook.DoesNotExist, Blog.DoesNotExist, StudyMaterial.DoesNotExist):
            return Response({"error": "Content not found."}, status=404)
        except Wallet.DoesNotExist:
            return Response({"error": f"{wallet_type.capitalize()} Wallet not found."}, status=404)

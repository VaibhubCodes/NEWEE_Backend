from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.db.models import Sum
from .models import Contest, Participant
from wallets.models import Wallet
from django.utils.timezone import now
from decimal import Decimal
from results.models import Participant as QuizParticipant
from .models import PrizeDistribution
from rest_framework import status
from .serializers import ContestSerializer
class JoinContestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, contest_id):
        try:
            # Fetch contest
            contest = Contest.objects.get(pk=contest_id)
            user = request.user

            # Check participation limit
            current_contests = Participant.objects.filter(user=user, contest__quiz=contest.quiz).count()
            if current_contests >= 3:
                return Response({"error": "You can participate in only 3 contests for the same quiz."}, status=400)

            # Check contest participant limit
            if contest.participants.count() >= contest.participant_limit:
                return Response({"error": "Contest is full. No more participants allowed."}, status=400)

            # Calculate total wallet balances
            discount_wallet = Wallet.objects.filter(user=user, wallet_type="discount").aggregate(balance=Sum("balance"))["balance"] or Decimal("0.00")
            winnings_wallet = Wallet.objects.filter(user=user, wallet_type="winnings").aggregate(balance=Sum("balance"))["balance"] or Decimal("0.00")
            earnexam_wallet = Wallet.objects.filter(user=user, wallet_type="earnexam").aggregate(balance=Sum("balance"))["balance"] or Decimal("0.00")

            total_balance = discount_wallet + winnings_wallet + earnexam_wallet

            # Check if user has enough balance
            entry_fee = contest.entry_fee
            if total_balance < entry_fee:
                return Response({"error": "Insufficient funds. Please add more money to participate."}, status=400)

            # Deduct from discount wallet first
            remaining_fee = entry_fee
            if discount_wallet > 0:
                deduction = min(discount_wallet, remaining_fee)
                Wallet.objects.filter(user=user, wallet_type="discount").update(balance=discount_wallet - deduction)
                remaining_fee -= deduction

            # Deduct from winnings wallet next
            if remaining_fee > 0 and winnings_wallet > 0:
                deduction = min(winnings_wallet, remaining_fee)
                Wallet.objects.filter(user=user, wallet_type="winnings").update(balance=winnings_wallet - deduction)
                remaining_fee -= deduction

            # Deduct from earnexam wallet last
            if remaining_fee > 0:
                Wallet.objects.filter(user=user, wallet_type="earnexam").update(balance=earnexam_wallet - remaining_fee)

            # Create participation entry
            Participant.objects.create(user=user, contest=contest)

            return Response({"message": "Successfully joined the contest!"}, status=201)

        except Contest.DoesNotExist:
            return Response({"error": "Contest not found."}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class DistributePrizesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, contest_id):
        try:
            contest = Contest.objects.get(pk=contest_id)

            # Ensure contest has ended
            if contest.end_time > now():
                return Response({"error": "Contest has not ended yet."}, status=400)

            # Fetch quiz participants and ranks
            quiz_participants = QuizParticipant.objects.filter(quiz=contest.quiz).order_by("rank")
            prize_distribution = PrizeDistribution.objects.filter(contest=contest).order_by("rank")

            # Allocate prizes to contest participants
            for prize in prize_distribution:
                if prize.rank <= len(quiz_participants):
                    quiz_participant = quiz_participants[prize.rank - 1]
                    participant = Participant.objects.get(contest=contest, user=quiz_participant.user)
                    participant.prize = prize.prize_amount
                    participant.save()

                    # Credit winnings wallet
                    winnings_wallet, _ = Wallet.objects.get_or_create(user=quiz_participant.user, wallet_type="winnings")
                    winnings_wallet.balance += prize.prize_amount
                    winnings_wallet.save()

            return Response({"message": "Prizes distributed successfully!"}, status=200)

        except Contest.DoesNotExist:
            return Response({"error": "Contest not found."}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Contest
from .serializers import ContestSerializer

class CreateContestView(APIView):
    """
    API view to create a new contest.
    """
    permission_classes = [IsAuthenticated]  # Restrict to admin users if required.

    def post(self, request):
        # Extract the data from the request
        data = request.data
        
        # Use a writable serializer to accept input for foreign key `quiz`
        serializer = ContestSerializer(data=data, context={"request": request})
        
        if serializer.is_valid():
            # Save the contest object if the data is valid
            contest = Contest.objects.create(
                title=data["title"],
                quiz_id=data["quiz"],  # Assuming `quiz` is sent as the quiz ID
                entry_fee=data["entry_fee"],
                participant_limit=data["participant_limit"],
                winner_percentage=data["winner_percentage"],
                start_time=data["start_time"],
                end_time=data["end_time"],
            )
            return Response(
                {
                    "message": "Contest created successfully!",
                    "data": ContestSerializer(contest).data,
                },
                status=status.HTTP_201_CREATED,
            )
        
        # Log the validation errors for debugging
        print("Validation Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UpdateContestView(APIView):
    """
    API view to update an existing contest.
    """
    permission_classes = [IsAuthenticated]  # Restrict to admin users if required.

    def put(self, request, contest_id):
        try:
            contest = Contest.objects.get(pk=contest_id)
        except Contest.DoesNotExist:
            return Response({"error": "Contest not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContestSerializer(contest, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Contest updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteContestView(APIView):
    """
    API view to delete an existing contest.
    """
    permission_classes = [IsAuthenticated]  # Restrict to admin users if required.

    def delete(self, request, contest_id):
        try:
            contest = Contest.objects.get(pk=contest_id)
            contest.delete()
            return Response({"message": "Contest deleted successfully!"}, status=status.HTTP_200_OK)
        except Contest.DoesNotExist:
            return Response({"error": "Contest not found."}, status=status.HTTP_404_NOT_FOUND)

class ContestListView(APIView):
    """
    API view to list all contests.
    """
    permission_classes = [AllowAny]  # Adjust permissions as required

    def get(self, request):
        contests = Contest.objects.all().select_related("quiz")  # Fetch contests with related quizzes
        serializer = ContestSerializer(contests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
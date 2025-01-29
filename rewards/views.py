from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import BlogReadingActivity, XamCoinSettings, ContestStreakReward, LockedXamCoins
from wallets.models import Wallet,Transaction
from blogs.models import Blog
from decimal import Decimal
from .models import ContestStreak
from .serializers import ContestStreakRewardSerializer


class StartReadingBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, blog_id):
        blog = Blog.objects.get(id=blog_id)
        activity, created = BlogReadingActivity.objects.get_or_create(
            user=request.user, blog=blog, defaults={"start_time": now()}
        )
        return Response({"message": "Reading session started", "activity_id": activity.id})

class UpdateReadingActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, activity_id):
        activity = BlogReadingActivity.objects.get(id=activity_id, user=request.user)
        time_spent = request.data.get("time_spent")  # Time in seconds
        is_active = request.data.get("is_active", True)

        if not is_active:
            activity.is_idle = True
            activity.save()
            return Response({"message": "User is idle. Coins counting paused."})

        activity.is_idle = False
        activity.total_time_spent += time_spent

        # Calculate coins earned
        coins_per_minute = Decimal(10.0)  # Default coins per minute
        thresholds = XamCoinSettings.objects.order_by("time_threshold")
        for threshold in thresholds:
            if activity.total_time_spent / 60 > threshold.time_threshold:
                coins_per_minute = threshold.coins_per_minute

        earned_coins = (Decimal(time_spent) / 60) * coins_per_minute
        activity.coins_earned += earned_coins
        activity.last_active_time = now()
        activity.save()

        return Response({
            "message": "Reading activity updated",
            "total_time_spent": activity.total_time_spent,
            "coins_earned": float(activity.coins_earned)  # Convert Decimal to float for JSON response
        })

class StopReadingBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, activity_id):
        activity = BlogReadingActivity.objects.get(id=activity_id, user=request.user)
        if activity.is_idle:
            activity.coins_earned = 0  # Nullify coins if idle for too long
        activity.save()
        return Response({
            "message": "Reading session stopped",
            "total_coins_earned": activity.coins_earned
        })


class ContestStreakView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            streak = ContestStreak.objects.get(user=user)
            response_data = {
                "streak_count": streak.streak_count,
                "last_participation_date": streak.last_participation_date,
                "bonus_earned": streak.bonus_earned,
            }
        except ContestStreak.DoesNotExist:
            response_data = {
                "streak_count": 0,
                "last_participation_date": None,
                "bonus_earned": 0,
            }

        return Response(response_data, status=200)

class ContestStreakProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            streak = ContestStreak.objects.get(user=user)
            locked_coins = LockedXamCoins.objects.get(user=user)

            next_settlement = ContestStreakReward.objects.filter(day__gt=locked_coins.last_settlement_day).first()

            return Response({
                "streak_count": streak.streak_count,
                "total_xamcoins_collected": streak.total_xamcoins_collected,
                "locked_xamcoins": locked_coins.total_locked,
                "last_settlement_day": locked_coins.last_settlement_day,
                "next_settlement_day": next_settlement.day if next_settlement else None,
                "next_bonus_percentage": next_settlement.bonus_percentage if next_settlement else None,
            }, status=200)
        except ContestStreak.DoesNotExist:
            return Response({"error": "No streak record found."}, status=404)
        except LockedXamCoins.DoesNotExist:
            return Response({"error": "No locked XamCoins record found."}, status=404)


class ContestStreakRewardListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        rewards = ContestStreakReward.objects.all()
        serializer = ContestStreakRewardSerializer(rewards, many=True)
        return Response(serializer.data, status=200)
    

class StreakSettlementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            streak = ContestStreak.objects.get(user=user)
            locked_coins = LockedXamCoins.objects.get(user=user)
            reward_day = ContestStreakReward.objects.filter(day=streak.streak_count).first()

            if not reward_day:
                return Response({"error": "No settlement available for the current streak day."}, status=400)

            # Calculate bonus
            bonus_percentage = reward_day.bonus_percentage / 100
            total_to_settle = locked_coins.total_locked * (1 + Decimal(bonus_percentage))

            # Credit to user's wallet
            wallet, _ = Wallet.objects.get_or_create(user=user, wallet_type="xamcoins")
            wallet.balance += total_to_settle
            wallet.save()

            # Log transaction
            Transaction.objects.create(
                wallet=wallet,
                transaction_type="credit",
                amount=total_to_settle,
                description=f"Contest Streak Settlement - Day {reward_day.day}"
            )

            # Reset locked coins
            locked_coins.total_locked = 0.00
            locked_coins.last_settlement_day = reward_day.day
            locked_coins.save()

            return Response({"message": f"XamCoins settled successfully with {reward_day.bonus_percentage}% bonus!", "total_settled": total_to_settle}, status=200)

        except ContestStreak.DoesNotExist:
            return Response({"error": "Streak record not found."}, status=404)
        except LockedXamCoins.DoesNotExist:
            return Response({"error": "No locked XamCoins found for the user."}, status=404)
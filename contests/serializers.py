from rest_framework import serializers
from .models import Contest, Participant, PrizeDistribution
from quizzes.serializers import QuizSerializer
from decimal import Decimal
from quizzes.models import Quiz

class ContestSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(), write_only=True)  # Allow quiz ID for input
    quiz_details = QuizSerializer(source='quiz', read_only=True)  # Use nested serializer for output
    total_prize_pool = serializers.SerializerMethodField()
    spots_left = serializers.SerializerMethodField()
    discounted_entry_fee = serializers.SerializerMethodField()

    class Meta:
        model = Contest
        fields = [
            "id",
            "title",
            "quiz",
            "quiz_details",  # Nested details for read-only
            "entry_fee",
            "discounted_entry_fee",
            "participant_limit",
            "spots_left",
            "winner_percentage",
            "start_time",
            "end_time",
            "total_prize_pool",
        ]

    def get_total_prize_pool(self, obj):
        try:
            entry_fee = Decimal(obj.entry_fee)  # Ensure entry_fee is a Decimal
            participant_limit = Decimal(obj.participant_limit)  # Ensure participant_limit is a Decimal
            admin_commission = Decimal(obj.admin_commission) / 100  # Ensure admin_commission is a Decimal
            total_pool = entry_fee * participant_limit
            return round(total_pool * (1 - admin_commission), 2)
        except Exception as e:
            raise TypeError(f"Error calculating total prize pool: {e}")

    def get_spots_left(self, obj):
        try:
            participant_limit = int(obj.participant_limit)  # Ensure it's an integer
            current_participants = obj.participants.count()  # Already an integer
            return participant_limit - current_participants
        except Exception as e:
            raise TypeError(f"Error calculating spots left: {e}")


    def get_discounted_entry_fee(self, obj):
        try:
            entry_fee = Decimal(obj.entry_fee)  # Ensure entry_fee is Decimal
            discount = Decimal("0.10")  # Example 10% discount
            return round(entry_fee * (1 - discount), 2)
        except Exception as e:
            raise TypeError(f"Error calculating discounted entry fee: {e}")


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = "__all__"

class PrizeDistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrizeDistribution
        fields = "__all__"

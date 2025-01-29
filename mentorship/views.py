from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Question, MentorAvailability, MentorshipSession, MentorshipSettings
from wallets.models import Wallet, Transaction
from questions.models import Subject
from datetime import timedelta
from django.contrib.auth import get_user_model
from mentorship.utils import generate_slots, filter_available_slots
from datetime import datetime

User = get_user_model()

class AskQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subject_id = request.data.get("subject_id")
        content = request.data.get("content")

        try:
            subject = Subject.objects.get(id=subject_id)
            settings = MentorshipSettings.objects.first()
            wallet = Wallet.objects.get(user=request.user, wallet_type="xamcoins")

            if wallet.balance < settings.cost_per_question:
                return Response({"error": "Insufficient XamCoins to ask the question."}, status=400)

            # Deduct XamCoins
            wallet.balance -= settings.cost_per_question
            wallet.save()

            # Log transaction
            Transaction.objects.create(
                wallet=wallet,
                transaction_type="debit",
                amount=settings.cost_per_question,
                description=f"Asked question on {subject.name}"
            )

            # Save question
            question = Question.objects.create(student=request.user, subject=subject, content=content)
            return Response({"message": "Question asked successfully.", "question_id": question.id}, status=200)

        except Subject.DoesNotExist:
            return Response({"error": "Subject not found."}, status=404)
        except Wallet.DoesNotExist:
            return Response({"error": "XamCoin wallet not found."}, status=404)



class AvailableSlotsView(APIView):
    """
    API to fetch available 30-minute and 60-minute slots for a mentor's availability.
    Excludes booked slots dynamically.
    """
    permission_classes = [AllowAny]

    def get(self, request, teacher_id):
        # Fetch mentor's availability
        availabilities = MentorAvailability.objects.filter(teacher_id=teacher_id, is_booked=False)

        # Collect booked slots
        booked_slots = MentorAvailability.objects.filter(teacher_id=teacher_id, is_booked=True)
        booked_intervals = [(slot.start_time, slot.end_time) for slot in booked_slots]

        all_thirty_min_slots = []
        all_sixty_min_slots = []

        for availability in availabilities:
            # Generate 30-minute and 60-minute slots
            thirty_min_slots, sixty_min_slots = generate_slots(availability)

            # Filter out overlapping slots
            available_thirty_min_slots = filter_available_slots(thirty_min_slots, booked_intervals)
            available_sixty_min_slots = filter_available_slots(sixty_min_slots, booked_intervals)

            all_thirty_min_slots.extend(available_thirty_min_slots)
            all_sixty_min_slots.extend(available_sixty_min_slots)

        return Response({
            "thirty_min_slots": [(slot[0].strftime("%Y-%m-%d %H:%M:%S"), slot[1].strftime("%Y-%m-%d %H:%M:%S")) for slot in all_thirty_min_slots],
            "sixty_min_slots": [(slot[0].strftime("%Y-%m-%d %H:%M:%S"), slot[1].strftime("%Y-%m-%d %H:%M:%S")) for slot in all_sixty_min_slots],
        })

class BookMentorshipSessionView(APIView):
    """
    API to book mentorship sessions with a teacher using dynamically generated slots.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        teacher_id = request.data.get("teacher_id")
        start_time_str = request.data.get("start_time")  # Start time of the slot in string format
        duration_minutes = int(request.data.get("duration_minutes"))  # Either 30 or 60 minutes

        try:
            # Convert start_time string to datetime
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")

            # Fetch mentorship settings
            settings = MentorshipSettings.objects.first()
            max_cost = settings.max_cost_30_minutes if duration_minutes == 30 else settings.max_cost_60_minutes

            # Fetch mentor's availability
            mentor_availabilities = MentorAvailability.objects.filter(teacher_id=teacher_id, is_booked=False)

            if not mentor_availabilities.exists():
                return Response({"error": "No availability found for the selected mentor."}, status=404)

            # Collect booked slots for the teacher
            booked_slots = MentorAvailability.objects.filter(teacher_id=teacher_id, is_booked=True)
            booked_intervals = [(slot.start_time, slot.end_time) for slot in booked_slots]

            # Generate available slots dynamically
            all_thirty_min_slots = []
            all_sixty_min_slots = []

            for availability in mentor_availabilities:
                thirty_min_slots, sixty_min_slots = generate_slots(availability)

                # Filter out overlapping slots
                available_thirty_min_slots = filter_available_slots(thirty_min_slots, booked_intervals)
                available_sixty_min_slots = filter_available_slots(sixty_min_slots, booked_intervals)

                all_thirty_min_slots.extend(available_thirty_min_slots)
                all_sixty_min_slots.extend(available_sixty_min_slots)

            # Check if the requested slot is valid and available
            requested_slot = (start_time, start_time + timedelta(minutes=duration_minutes))
            if duration_minutes == 30:
                if requested_slot not in all_thirty_min_slots:
                    return Response({"error": "The selected 30-minute slot is unavailable."}, status=400)
            elif duration_minutes == 60:
                if requested_slot not in all_sixty_min_slots:
                    return Response({"error": "The selected 60-minute slot is unavailable."}, status=400)

            # Check student's wallet balance
            wallet = Wallet.objects.get(user=request.user, wallet_type="xamcoins")
            if wallet.balance < max_cost:
                return Response({"error": "Insufficient XamCoins to book the session."}, status=400)

            # Deduct XamCoins
            wallet.balance -= max_cost
            wallet.save()

            # Log transaction
            Transaction.objects.create(
                wallet=wallet,
                transaction_type="debit",
                amount=max_cost,
                description=f"Booked mentorship session with teacher ID {teacher_id}"
            )

            # Mark the slot as booked
            MentorAvailability.objects.create(
                teacher_id=teacher_id,
                start_time=requested_slot[0],
                end_time=requested_slot[1],
                is_booked=True
            )

            # Create mentorship session
            session = MentorshipSession.objects.create(
                student=request.user,
                teacher_id=teacher_id,
                start_time=requested_slot[0],
                duration_minutes=duration_minutes,
                cost=max_cost,
                is_confirmed=True
            )

            return Response({"message": "Mentorship session booked successfully.", "session_id": session.id}, status=200)

        except MentorAvailability.DoesNotExist:
            return Response({"error": "Mentor availability not found."}, status=404)
        except Wallet.DoesNotExist:
            return Response({"error": "XamCoin wallet not found."}, status=404)
        except ValueError:
            return Response({"error": "Invalid date format for start_time. Use 'YYYY-MM-DD HH:MM:SS'."}, status=400)
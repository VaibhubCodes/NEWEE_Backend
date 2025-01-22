from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import Participant, Answer, Leaderboard
from .serializers import ParticipantSerializer, LeaderboardSerializer
from quizzes.models import Quiz, SectionQuestion
from django.utils.timezone import now
import logging
logger = logging.getLogger(__name__)

class StartQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(pk=quiz_id)

            # Create participant if not already exists
            participant, created = Participant.objects.get_or_create(
                user=request.user, quiz=quiz
            )
            if not created:
                return Response(
                    {"error": "You have already started this quiz."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response({"participant_id": participant.id, "message": "Quiz started successfully!"})
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)




class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, participant_id):
        try:
            participant = Participant.objects.get(pk=participant_id, user=request.user)
            question_id = request.data.get("section_question")
            selected_option = request.data.get("selected_option")

            section_question = SectionQuestion.objects.get(pk=question_id)
            Answer.objects.create(participant=participant, section_question=section_question, selected_option=selected_option)
            participant.calculate_score_and_accuracy()
            return Response({"message": "Answer submitted successfully!"})
        except Participant.DoesNotExist:
            return Response({"error": "Participant not found."}, status=404)
        except SectionQuestion.DoesNotExist:
            return Response({"error": "SectionQuestion not found."}, status=404)


class FinalizeQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, participant_id):
        try:
            logger.info(f"Finalizing quiz for participant ID: {participant_id}")
            participant = Participant.objects.get(pk=participant_id, user=request.user)

            if not participant.completed_at:
                participant.handle_unanswered_questions()
                participant.completed_at = now()
                participant.calculate_score_and_accuracy()
                participant.save(update_fields=['completed_at'])

            logger.info(f"Quiz finalized for participant ID: {participant_id}")
            return Response({"message": "Quiz finalized successfully!"})
        except Participant.DoesNotExist:
            return Response({"error": "Participant not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error finalizing quiz: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class LeaderboardView(APIView):
    permission_classes = [AllowAny]  # Allow all participants to access the leaderboard

    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            participants = Participant.objects.filter(quiz=quiz)

            # Rank participants: Highest score first, then fastest completion time
            sorted_participants = sorted(
                participants,
                key=lambda p: (-p.score, p.get_time_taken() or float('inf'))
            )

            # Assign rank based on sorted order
            leaderboard_data = []
            rank = 1
            for participant in sorted_participants:
                leaderboard_data.append({
                    "id": participant.id,
                    "user_name": participant.user.username,
                    "score": participant.score,
                    "rank": rank,
                    "correct_answers": participant.correct_answers,
                    "time_taken": str(participant.get_time_taken() or "N/A"),
                })
                rank += 1

            return Response(leaderboard_data, status=200)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)



class ParticipantResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, participant_id):
        try:
            participant = Participant.objects.get(pk=participant_id, user=request.user)
            if not participant.result_status:
                return Response({"error": "Results are not yet published by the admin."}, status=403)
            serializer = ParticipantSerializer(participant)
            return Response(serializer.data)
        except Participant.DoesNotExist:
            return Response({"error": "Participant not found."}, status=404)

class ParticipantDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, participant_id):
        try:
            participant = Participant.objects.get(pk=participant_id, user=request.user)
            return Response({
                "id": participant.id,
                "name": participant.user.username,  # Adjust as needed
                "quiz": participant.quiz.title
            })
        except Participant.DoesNotExist:
            return Response({"error": "Participant not found"}, status=404)
        
class QuizStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            participant = Participant.objects.filter(user=request.user, quiz=quiz).first()

            if participant:
                return Response({
                    "quiz_id": quiz_id,
                    "participant_id": participant.id,
                    "is_completed": bool(participant.completed_at),
                })
            else:
                return Response({
                    "quiz_id": quiz_id,
                    "participant_id": None,
                    "is_completed": False,
                })
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found."}, status=404)
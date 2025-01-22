from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Quiz, Section, SectionQuestion
from .serializers import QuizSerializer, SectionSerializer, SectionQuestionSerializer
from questions.models import Question


class SectionListView(APIView):
    def get(self, request):
        sections = Section.objects.all()
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)

    def post(self, request):
        print("Received Payload:", request.data)  # Log the payload
        serializer = SectionSerializer(data=request.data)
        if serializer.is_valid():
            section = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Errors:", serializer.errors)  # Log validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizSectionsView(APIView):
    """
    Manage sections related to a specific quiz.
    """
    def get(self, request, quiz_id):
        try:
            sections = Section.objects.filter(quiz_id=quiz_id)
            serializer = SectionSerializer(sections, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        data['quiz'] = quiz.id  # Ensure the quiz ID is included in the payload
        serializer = SectionSerializer(data=data)
        if serializer.is_valid():
            section = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# In views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Section, SectionQuestion
from questions.models import Question
from .serializers import SectionQuestionSerializer, QuestionSerializer

class SectionQuestionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, section_id):
        try:
            section = Section.objects.get(pk=section_id)
            section_questions = section.section_questions.all()
            serializer = SectionQuestionSerializer(section_questions, many=True)
            return Response(serializer.data)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=404)

class AddQuestionsToSectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, section_id):
        if not isinstance(request.data, dict):
            return Response({"error": "Invalid input format. Expected a JSON object."}, status=400)

        try:
            section = Section.objects.get(pk=section_id)
            question_ids = request.data.get("question_ids", [])
            marks = request.data.get("marks")

            if not question_ids or not marks:
                return Response({"error": "Both question_ids and marks are required."}, status=400)

            for question_id in question_ids:
                question = Question.objects.get(pk=question_id)
                SectionQuestion.objects.create(section=section, question=question, marks=marks)

            return Response({"message": "Questions added successfully."}, status=201)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=404)
        except Question.DoesNotExist:
            return Response({"error": "One or more questions not found."}, status=404)



class QuizListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            serializer = QuizSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
            quiz_data = request.data
            sections_data = quiz_data.pop('sections', None)  # Extract sections from request data

            serializer = QuizSerializer(quiz, data=quiz_data, partial=True)
            if serializer.is_valid():
                quiz = serializer.save()

                # If sections are provided, update them
                if sections_data is not None:
                    quiz.sections.clear()  # Remove existing section associations
                    for section_id in sections_data:
                        try:
                            section = Section.objects.get(id=section_id)
                            section.quiz = quiz
                            section.save()
                        except Section.DoesNotExist:
                            return Response(
                                {"error": f"Section with id {section_id} does not exist."},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)


class SectionQuestionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, section_id):
        try:
            section = Section.objects.get(pk=section_id)
            section_questions = section.section_questions.all()
            serializer = SectionQuestionSerializer(section_questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=status.HTTP_404_NOT_FOUND)
        
class UpdateSectionQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, section_id):
        try:
            section = Section.objects.get(pk=section_id)
            question_ids = request.data.get("question_ids", [])
            marks = request.data.get("marks")

            if not question_ids or not marks:
                return Response({"error": "Both question_ids and marks are required."}, status=400)

            # Clear existing questions
            SectionQuestion.objects.filter(section=section).delete()

            # Add updated questions
            for question_id in question_ids:
                question = Question.objects.get(pk=question_id)
                SectionQuestion.objects.create(section=section, question=question, marks=marks)

            return Response({"message": "Questions updated successfully."}, status=200)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=404)
        except Question.DoesNotExist:
            return Response({"error": "One or more questions not found."}, status=404)
        
class CreateQuizView(APIView):
    """
    View to handle quiz creation with associated sections and quiz types.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract quiz data from the request
        quiz_data = request.data
        sections_data = quiz_data.pop('sections', [])  # Remove sections from quiz data
        
        # Serialize and save the quiz
        quiz_serializer = QuizSerializer(data=quiz_data)
        if quiz_serializer.is_valid():
            quiz = quiz_serializer.save()
        else:
            return Response(quiz_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Process and save associated sections
        for section_id in sections_data:
            try:
                section = Section.objects.get(id=section_id)
                section.quiz = quiz  # Link section to the created quiz
                section.save()
            except Section.DoesNotExist:
                return Response(
                    {"error": f"Section with id {section_id} does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(quiz_serializer.data, status=status.HTTP_201_CREATED)
    
class QuizTypesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        quiz_types = [{"key": key, "label": label} for key, label in Quiz.QUIZ_TYPES]
        return Response(quiz_types)
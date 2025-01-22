from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import Exam, Section,SectionQuestion
from questions.models import Question
from .serializers import ExamSerializer, SectionSerializer,SectionQuestionSerializer
from rest_framework import status

class ExamListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        exams = Exam.objects.all()
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)

    def post(self, request):
        print("Received Payload:", request.data)  # Debug the payload
        serializer = ExamSerializer(data=request.data)
        if serializer.is_valid():
            exam = serializer.save()

            # Map existing sections to the exam
            section_ids = request.data.get('sections', [])
            if section_ids:
                sections = Section.objects.filter(id__in=section_ids)
                sections.update(exam=exam)  # Associate sections with the exam

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Errors:", serializer.errors)  # Log errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ExamDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            exam = Exam.objects.get(pk=pk)
            serializer = ExamSerializer(exam)
            return Response(serializer.data)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=404)

class SectionDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            section = Section.objects.get(pk=pk)
            serializer = SectionSerializer(section)
            return Response(serializer.data)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=404)

class SectionQuestionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, section_id):
        try:
            section = Section.objects.get(pk=section_id)
            section_questions = section.section_questions.all()  # Fetch related SectionQuestions
            serializer = SectionQuestionSerializer(section_questions, many=True)
            return Response(serializer.data)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=404)

class AddSectionQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, section_id):
        try:
            section = Section.objects.get(pk=section_id)
            question_ids = request.data.get("question_ids", [])
            marks = request.data.get("marks")

            if not question_ids or not marks:
                return Response({"error": "Both question_ids and marks are required"}, status=400)

            for question_id in question_ids:
                question = Question.objects.get(pk=question_id)
                SectionQuestion.objects.create(section=section, question=question, marks=marks)

            return Response({"message": "Questions added successfully"}, status=201)
        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=404)
        except Question.DoesNotExist:
            return Response({"error": f"One or more questions not found"}, status=404)
        
class SectionListView(APIView):
    def get(self, request):
        sections = Section.objects.all()
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)
    
class SectionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

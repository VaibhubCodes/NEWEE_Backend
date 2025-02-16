
from .serializers import AIQuizSerializer
from rest_framework.generics import RetrieveAPIView
import time
import logging
import openai
from pdfminer.high_level import extract_text
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import UploadedPDF, AIQuiz, AIQuestion
from questions.models import Subject, Chapter, Topic
from .utils import generate_questions_with_openai

logger = logging.getLogger(__name__)

class UploadPDFView(APIView):
    """Upload a PDF and trigger AI quiz generation asynchronously."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            uploaded_file = request.FILES.get("pdf")
            subject_id = request.data.get("subject_id")
            chapter_id = request.data.get("chapter_id", None)
            topic_id = request.data.get("topic_id", None)
            num_questions = int(request.data.get("num_questions", 10))
            difficulty = request.data.get("difficulty", "Medium")
            include_explanations = request.data.get("include_explanations", "false").lower() == "true"

            # Validate Subject
            try:
                subject = Subject.objects.get(id=subject_id)
                chapter = Chapter.objects.get(id=chapter_id) if chapter_id else None
                topic = Topic.objects.get(id=topic_id) if topic_id else None
            except Subject.DoesNotExist:
                return Response({"error": "Invalid subject ID"}, status=400)

            # Ensure the PDF is uploaded
            if not uploaded_file:
                return Response({"error": "No PDF file provided"}, status=400)

            pdf_instance = UploadedPDF.objects.create(user=request.user, file=uploaded_file)

            # 📌 Start timing PDF text extraction
            start_time_extraction = time.time()

            # Extract text using pdfminer.six (FAST)
            text = extract_text(pdf_instance.file.path)

            # 📌 End timing PDF text extraction
            extraction_time = time.time() - start_time_extraction
            logger.info(f"✅ PDF Text Extraction Time: {extraction_time:.2f} seconds")

            # 📌 Start timing OpenAI question generation
            start_time_ai = time.time()

            # Generate questions using Parallel OpenAI Calls
            questions_data = generate_questions_with_openai(text, num_questions, difficulty, include_explanations)

            # 📌 End timing OpenAI question generation
            ai_generation_time = time.time() - start_time_ai
            logger.info(f"✅ AI Quiz Question Generation Time: {ai_generation_time:.2f} seconds")

            # Ensure questions_data is a list
            if not isinstance(questions_data, list):
                return Response({"error": "Invalid response from AI"}, status=500)

            # Store in database
            quiz = AIQuiz.objects.create(user=request.user, subject=subject, chapter=chapter, topic=topic)

            for question in questions_data:
                AIQuestion.objects.create(
                    quiz=quiz,
                    text=question["text"],
                    option1=question["option1"],
                    option2=question["option2"],
                    option3=question["option3"],
                    option4=question["option4"],
                    correct_answer=question["correct_answer"],
                    explanation=question.get("explanation", "")
                )

            return Response({
                "message": "Quiz generated successfully",
                "quiz_id": quiz.id,
                "pdf_extraction_time": f"{extraction_time:.2f} seconds",
                "ai_generation_time": f"{ai_generation_time:.2f} seconds"
            })

        except Exception as e:
            logger.error(f"Unexpected error in /api/ai/upload-pdf/: {str(e)}")
            return Response({"error": "Internal Server Error"}, status=500)



class MyGeneratedQuizzesView(APIView):
    """Retrieve all AI-generated quizzes along with questions."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all quizzes created by the logged-in user
        quizzes = AIQuiz.objects.filter(user=request.user).order_by('-generated_at')

        # Serialize quizzes
        serializer = AIQuizSerializer(quizzes, many=True)
        return Response(serializer.data)

class GetQuizView(RetrieveAPIView):
    """API to retrieve AI-generated quiz details including questions."""
    queryset = AIQuiz.objects.all()
    serializer_class = AIQuizSerializer
    permission_classes = [AllowAny]
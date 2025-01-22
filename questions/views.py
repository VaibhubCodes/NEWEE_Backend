from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from .models import Subject, Chapter, Topic, Category, Question
import csv
import io
from datetime import timedelta
from django.utils.timezone import now
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    SubjectSerializer,
    ChapterSerializer,
    TopicSerializer,
    CategorySerializer,
    QuestionSerializer,
)

class SubjectListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

class ChapterListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        chapters = Chapter.objects.all()
        serializer = ChapterSerializer(chapters, many=True)
        return Response(serializer.data)

class TopicListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        topics = Topic.objects.all()
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data)

class QuestionListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filters = {}
        if "subject" in request.query_params:
            filters["subject__name__iexact"] = request.query_params["subject"]
        if "chapter" in request.query_params:
            filters["chapter__name__iexact"] = request.query_params["chapter"]
        if "topic" in request.query_params:
            filters["topic__name__iexact"] = request.query_params["topic"]
        if "difficulty" in request.query_params:
            filters["difficulty"] = request.query_params["difficulty"]
        if "category" in request.query_params:
            filters["category__name__iexact"] = request.query_params["category"]

        questions = Question.objects.filter(**filters)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    


class RecentQuestionsView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict to authenticated users

    def get(self, request):
        # Get questions uploaded in the last 5 minutes
        time_threshold = now() - timedelta(minutes=5)
        recent_questions = Question.objects.filter(created_at__gte=time_threshold).select_related(
            'category', 'subject', 'chapter', 'topic'
        )
        
        serialized_questions = []

        for question in recent_questions:
            serialized_questions.append({
                "text": question.text,
                "category": question.category.name if question.category else None,
                "subject": question.subject.name if question.subject else None,
                "chapter": question.chapter.name if question.chapter else None,
                "topic": question.topic.name if question.topic else None,
                "difficulty": question.difficulty,
            })

        return Response(serialized_questions, status=200)

class BulkUploadQuestionsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = io.StringIO(file.read().decode("utf-8"))
            reader = csv.DictReader(data)
            errors = []
            success_count = 0

            for row_number, row in enumerate(reader, start=2):  # Start from row 2
                try:
                    # Validate and map IDs directly
                    subject = Subject.objects.get(id=row["subject_id"].strip())
                    chapter = Chapter.objects.get(id=row["chapter_id"].strip()) if row.get("chapter_id") else None
                    topic = Topic.objects.get(id=row["topic_id"].strip()) if row.get("topic_id") else None

                    # Create the question
                    question = Question(
                        text=row["text"].strip(),
                        question_type=row.get("question_type", "MCQ").strip(),  # Default to MCQ
                        difficulty=row["difficulty"].strip(),
                        category=Category.objects.get(name=row["category"].strip()),
                        subject=subject,
                        chapter=chapter,
                        topic=topic,
                        correct_answer=row["correct_answer"].strip(),
                        option1=row["option1"].strip(),
                        option2=row["option2"].strip(),
                        option3=row["option3"].strip(),
                        option4=row["option4"].strip(),
                    )
                    question.clean()  # Validate the question
                    question.save()
                    success_count += 1
                except Exception as e:
                    errors.append({"row": row_number, "error": str(e)})

            return Response(
                {
                    "message": "Bulk upload completed.",
                    "success_count": success_count,
                    "errors": errors,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryListView(APIView):
    """
    View to list all categories.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class FilteredQuestionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filters = {}
        if 'subject' in request.query_params:
            filters['subject__id'] = request.query_params['subject']
        if 'chapter' in request.query_params:
            filters['chapter__id'] = request.query_params['chapter']
        if 'topic' in request.query_params:
            filters['topic__id'] = request.query_params['topic']

        questions = Question.objects.filter(**filters)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

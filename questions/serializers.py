from rest_framework import serializers
from .models import Subject, Chapter, Topic, Category, Question

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "description"]

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ["id", "name", "subject"]

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "name", "chapter"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]

class QuestionSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    chapter = ChapterSerializer()
    topic = TopicSerializer()
    category = CategorySerializer()

    class Meta:
        model = Question
        fields = [
            "id", "text", "image", "category", "subject", "chapter", "topic",
            "difficulty", "question_type", "option1", "option2", "option3", "option4", "correct_answer",
        ]
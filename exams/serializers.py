from rest_framework import serializers
from .models import Exam, Section, SectionQuestion
from questions.serializers import QuestionSerializer

class SectionQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = SectionQuestion
        fields = ['id', 'question', 'marks']

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'title', 'description', 'marks']


class ExamSerializer(serializers.ModelSerializer):
    sections = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Section.objects.all(), required=False
    )

    class Meta:
        model = Exam
        fields = [
            'id', 'title', 'description', 'subject', 'total_marks',
            'duration_minutes', 'scheduled_at', 'is_active', 'sections'
        ]


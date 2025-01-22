from rest_framework import serializers
from .models import Quiz, Section, SectionQuestion
from questions.serializers import QuestionSerializer



class SectionQuestionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    
    class Meta:
        model = SectionQuestion
        fields = ['id', 'question', 'marks']


class SectionSerializer(serializers.ModelSerializer):
    section_questions = SectionQuestionSerializer(many=True, read_only=True)  # Nested questions
    question_marks = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            'id', 
            'name', 
            'description', 
            'num_questions', 
            'total_marks', 
            'question_marks', 
            'section_questions',
            'is_active'
        ]

    def get_question_marks(self, obj):
        return obj.calculate_question_marks()
    


class QuizSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'quiz_type',
            'is_active',
            'start_date',
            'end_date',
            'sections',
        ]

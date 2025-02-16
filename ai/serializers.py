from rest_framework import serializers
from .models import AIQuiz, AIQuestion

class AIQuestionSerializer(serializers.ModelSerializer):
    """Serializer for AI-generated questions."""
    
    class Meta:
        model = AIQuestion
        fields = [
            'id', 'quiz', 'text', 'option1', 'option2', 'option3', 'option4', 
            'correct_answer', 'difficulty', 'explanation'
        ]

class AIQuizSerializer(serializers.ModelSerializer):
    """Serializer for AI-generated quizzes with associated questions."""
    
    questions = AIQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = AIQuiz
        fields = [
            'id', 'user', 'subject', 'chapter', 'topic', 'generated_at', 
            'is_finalized', 'questions'
        ]

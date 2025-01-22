from rest_framework import serializers
from .models import Participant, Answer, Leaderboard


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'section_question', 'selected_option', 'is_correct', 'marks_obtained']


class ParticipantSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    time_taken = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = [
            'id', 'user', 'quiz', 'started_at', 'completed_at',
            'score', 'total_marks', 'correct_answers', 'rank', 'result_status', 'answers','time_taken'
        ]
    def get_time_taken(self, obj):
        return str(obj.get_time_taken())

class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaderboard
        fields = ['id', 'quiz', 'generated_at']

class ParticipantDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Assuming you want the username as a string
    quiz = serializers.StringRelatedField()  # Assuming you want the quiz title as a string

    class Meta:
        model = Participant
        fields = ['id', 'user', 'quiz', 'score', 'correct_answers', 'rank', 'completed_at']

from rest_framework import serializers
from .models import Question, MentorshipSession, MentorAvailability, MentorshipSettings
from quizzes.models import Subject
from users.models import CustomUser

# Serializer for MentorshipSettings
class MentorshipSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorshipSettings
        fields = ['cost_per_question', 'max_cost_30_minutes', 'max_cost_60_minutes']


# Serializer for Questions
class QuestionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'student', 'student_name', 'subject', 'subject_name', 'content', 'created_at', 'answered']


# Serializer for MentorAvailability
class MentorAvailabilitySerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = MentorAvailability
        fields = ['id', 'teacher', 'teacher_name', 'start_time', 'end_time', 'is_booked']


# Serializer for MentorshipSession
class MentorshipSessionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = MentorshipSession
        fields = [
            'id', 'student', 'student_name', 'teacher', 'teacher_name', 
            'start_time', 'duration_minutes', 'cost', 'is_confirmed'
        ]

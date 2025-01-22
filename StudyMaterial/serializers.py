from rest_framework import serializers
from .models import StudyMaterial, Lesson, Enrollment

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_type', 'video_url', 'pdf_file', 'created_at']

class StudyMaterialSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'description', 'subject', 'chapter', 'topic', 'is_paid', 'price', 'created_at', 'updated_at', 'lessons']

class EnrollmentSerializer(serializers.ModelSerializer):
    study_material = StudyMaterialSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'study_material', 'enrolled_at', 'payment_status']

from rest_framework import serializers
from .models import CustomUser, Teacher, Student

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['school_id', 'location']


class StudentSerializer(serializers.ModelSerializer):
    class_name = serializers.ChoiceField(choices=Student.CLASS_CHOICES)  # Enforces valid options

    class Meta:
        model = Student
        fields = ['school_id', 'address', 'date_of_birth', 'location', 'class_name', 'profile_picture']


class UserSerializer(serializers.ModelSerializer):
    teacher_profile = TeacherSerializer(required=False, allow_null=True)
    student_profile = StudentSerializer(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'name', 'phone', 'role',
            'pan_number', 'upi_id', 'aadhar_number', 'latitude', 'longitude',
            'teacher_profile', 'student_profile'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'phone', 'role', 'password']

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

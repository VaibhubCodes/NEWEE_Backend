from django.contrib import admin
from .models import CustomUser, Teacher, Student

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'name', 'phone', 'role', 'is_active', 'is_staff')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_id', 'location')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_id', 'address', 'date_of_birth', 'location', 'class_name')  # Updated fields


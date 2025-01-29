from django.contrib import admin
from .models import StudyMaterial, Lesson, Enrollment

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'is_premium', 'unlock_cost', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('subject', 'is_premium', 'created_at')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'study_material', 'lesson_type', 'created_at')
    list_filter = ('lesson_type',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'study_material', 'enrolled_at', 'payment_status')
    list_filter = ('payment_status',)

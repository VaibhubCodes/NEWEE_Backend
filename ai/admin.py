from django.contrib import admin
from .models import AIQuiz, AIQuestion, UploadedPDF

@admin.register(UploadedPDF)
class UploadedPDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'file', 'uploaded_at')
    search_fields = ('user__email',)
    list_filter = ('uploaded_at',)

@admin.register(AIQuiz)
class AIQuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'chapter', 'topic', 'generated_at', 'is_finalized')
    list_filter = ('generated_at', 'is_finalized', 'subject')
    search_fields = ('user__email', 'subject__name', 'chapter__name', 'topic__name')

@admin.register(AIQuestion)
class AIQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'text', 'difficulty', 'correct_answer')
    search_fields = ('text', 'quiz__subject__name', 'quiz__chapter__name', 'quiz__topic__name')
    list_filter = ('difficulty',)

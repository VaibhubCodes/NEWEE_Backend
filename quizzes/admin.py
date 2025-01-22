from django.contrib import admin
from .models import Quiz, Section, SectionQuestion


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1


class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")
    inlines = [SectionInline]


class SectionQuestionAdmin(admin.ModelAdmin):
    list_display = ('section', 'question', 'marks') 


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Section)
admin.site.register(SectionQuestion, SectionQuestionAdmin)

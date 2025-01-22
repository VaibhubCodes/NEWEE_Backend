from django.contrib import admin
from django import forms
from .models import Exam, Section, SectionQuestion
from questions.models import Question, Subject
from django.db import models


class SectionQuestionAdminForm(forms.ModelForm):
    """
    Custom form for the SectionQuestion model in the admin.
    Allows filtering questions by subject and bulk assigning marks to selected questions.
    """
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=True,
        label="Subject",
        help_text="Filter questions by subject.",
    )
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.none(),
        required=True,
        widget=admin.widgets.FilteredSelectMultiple("Questions", is_stacked=False),
        help_text="Select questions to add to this section.",
    )
    marks = forms.IntegerField(
        required=True,
        label="Marks",
        help_text="Assign the same marks to all selected questions.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "subject" in self.data:  # Dynamically filter questions by subject
            try:
                subject_id = int(self.data.get("subject"))
                self.fields["questions"].queryset = Question.objects.filter(subject_id=subject_id)
            except (ValueError, TypeError):
                self.fields["questions"].queryset = Question.objects.none()
        elif self.instance.pk:  # When editing an existing instance
            self.fields["questions"].queryset = Question.objects.filter(subject=self.instance.section.exam.subject)

    class Meta:
        model = SectionQuestion
        fields = ["section", "subject", "questions", "marks"]


class SectionQuestionInline(admin.TabularInline):
    """
    Inline for managing Section Questions directly within the Section admin.
    """
    model = SectionQuestion
    fields = ("question", "marks")
    readonly_fields = ("question",)
    extra = 0
    can_delete = True


class SectionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Sections.
    Includes inline management of Section Questions.
    """
    list_display = ("title", "exam", "get_total_marks", "get_question_count")
    list_filter = ("exam",)
    search_fields = ("title", "exam__title")
    inlines = [SectionQuestionInline]

    def get_total_marks(self, obj):
        """
        Custom method to calculate total marks for a section.
        """
        return obj.section_questions.aggregate(total=models.Sum("marks"))["total"] or 0
    get_total_marks.short_description = "Total Marks"

    def get_question_count(self, obj):
        """
        Custom method to count the number of questions in a section.
        """
        return obj.section_questions.count()
    get_question_count.short_description = "Number of Questions"


class SectionInline(admin.TabularInline):
    """
    Inline for managing Sections directly within the Exam admin.
    """
    model = Section
    extra = 1


class ExamAdmin(admin.ModelAdmin):
    """
    Admin interface for Exams.
    Includes inline management of Sections.
    """
    list_display = ("title", "subject", "scheduled_at", "is_active", "get_section_count")
    list_filter = ("is_active", "subject", "scheduled_at")
    search_fields = ("title", "subject__name")
    inlines = [SectionInline]

    def get_section_count(self, obj):
        """
        Custom method to count the number of sections in an exam.
        """
        return obj.sections.count()
    get_section_count.short_description = "Number of Sections"


class SectionQuestionAdmin(admin.ModelAdmin):
    """
    Custom admin for the SectionQuestion model.
    Includes functionality to add multiple questions with the same marks.
    """
    form = SectionQuestionAdminForm
    list_display = ("section", "question", "marks")

    def save_model(self, request, obj, form, change):
        """
        Override save_model to handle multiple questions and assign marks.
        """
        if change:  # Editing an existing entry
            super().save_model(request, obj, form, change)
        else:  # Adding new entries
            section = form.cleaned_data["section"]
            subject = form.cleaned_data["subject"]
            questions = form.cleaned_data["questions"]
            marks = form.cleaned_data["marks"]

            for question in questions:
                SectionQuestion.objects.create(
                    section=section,
                    question=question,
                    marks=marks,
                )

    def get_queryset(self, request):
        """
        Customize queryset to prefetch related objects for better performance.
        """
        qs = super().get_queryset(request)
        return qs.select_related("section", "question")


# Register models with admin
admin.site.register(Exam, ExamAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionQuestion, SectionQuestionAdmin)

from django.db import models
from questions.models import Question, Subject

class Exam(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the exam")
    description = models.TextField(null=True, blank=True, help_text="Short description of the exam")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name="exams")
    total_marks = models.PositiveIntegerField(help_text="Total marks for the exam")
    duration_minutes = models.PositiveIntegerField(help_text="Duration of the exam in minutes")
    scheduled_at = models.DateTimeField(help_text="Scheduled date and time for the exam")
    is_active = models.BooleanField(default=False, help_text="Status of the exam (active or not)")

    def __str__(self):
        return self.title


class Section(models.Model):
    exam = models.ForeignKey(
        Exam, on_delete=models.SET_NULL, null=True, blank=True, related_name="sections"
    )
    title = models.CharField(max_length=255, help_text="Title of the section")
    description = models.TextField(null=True, blank=True, help_text="Description of the section")
    marks = models.PositiveIntegerField(help_text="Total marks for the section")

    def __str__(self):
        return f"{self.title} ({self.exam.title if self.exam else 'No Exam'})"


class SectionQuestion(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="section_questions")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="section_questions")
    marks = models.PositiveIntegerField(help_text="Marks assigned to this question")

    def __str__(self):
        return f"{self.section.title} - {self.question.text[:50]}"

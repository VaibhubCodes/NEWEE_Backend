from django.db import models
from questions.models import Question


class Quiz(models.Model):
    QUIZ_TYPES = [
        ('P2P', 'Peer-to-Peer Battle'),
        ('MEGA', 'Mega Contest'),
        ('GROUP', 'Group Battle'),
        ('DAILY', 'Daily Quiz'),
        ('OLYMPIAD', 'Olympiad'),
        ('SELF', 'Self Challenge'),
        ('EXAM', 'Exam'),
    ]

    title = models.CharField(max_length=255, help_text="Title of the quiz")
    description = models.TextField(blank=True, help_text="Short description of the quiz")
    quiz_type = models.CharField(max_length=50, choices=QUIZ_TYPES, default='DAILY')
    is_active = models.BooleanField(default=False, help_text="Activate or deactivate the quiz")
    start_date = models.DateTimeField(null=True, blank=True, help_text="Start date and time of the quiz")
    end_date = models.DateTimeField(null=True, blank=True, help_text="End date and time of the quiz")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Section(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True, related_name="sections")
    name = models.CharField(max_length=255, help_text="Name of the section")
    description = models.TextField(blank=True, help_text="Description of the section")
    num_questions = models.PositiveIntegerField(help_text="Number of questions in the section")
    total_marks = models.PositiveIntegerField(help_text="Total marks for the section")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def calculate_question_marks(self):
        if self.num_questions > 0:
            return self.total_marks / self.num_questions
        return 0


class SectionQuestion(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="section_questions")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="quizzes_section_questions")
    marks = models.PositiveIntegerField(help_text="Marks assigned to this question")

    def __str__(self):
        return f"{self.section.name} - {self.question.text[:50]}"

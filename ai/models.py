from django.db import models
from django.contrib.auth import get_user_model
from questions.models import Subject, Chapter, Topic

User = get_user_model()

class UploadedPDF(models.Model):
    """Stores uploaded PDFs for quiz generation."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="pdfs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PDF Uploaded by {self.user.name}"

class AIQuiz(models.Model):
    """Stores AI-generated quizzes."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="ai_quizzes")
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, related_name="ai_quizzes", blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, related_name="ai_quizzes", blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_finalized = models.BooleanField(default=False)

    def __str__(self):
        return f"Quiz for {self.subject.name} - {self.chapter.name if self.chapter else 'General'}"

class AIQuestion(models.Model):
    """Stores AI-generated MCQs."""
    DIFFICULTY_CHOICES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]

    quiz = models.ForeignKey(AIQuiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="medium")
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=10, choices=[("option1", "Option 1"), ("option2", "Option 2"), ("option3", "Option 3"), ("option4", "Option 4")])
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text

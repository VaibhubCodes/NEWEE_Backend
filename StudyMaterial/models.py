from django.db import models
from django.contrib.auth import get_user_model
from questions.models import Subject, Chapter, Topic

User = get_user_model()

class StudyMaterial(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="study_materials")
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name="study_materials")
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="study_materials")
    is_paid = models.BooleanField(default=False, help_text="Is this course paid?")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Price if paid course")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
    ]

    study_material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPE_CHOICES)
    video_url = models.URLField(blank=True, null=True, help_text="Provide a video URL for video lessons.")
    pdf_file = models.FileField(upload_to='study_material/lessons/', blank=True, null=True, help_text="Upload a PDF for PDF lessons.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.lesson_type})"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    study_material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('completed', 'Completed')],
        default='pending'
    )

    class Meta:
        unique_together = ('student', 'study_material')

    def __str__(self):
        return f"{self.student} enrolled in {self.study_material.title}"

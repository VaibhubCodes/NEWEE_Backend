from django.db import models
from django.core.exceptions import ValidationError

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="chapters")

    class Meta:
        unique_together = ("name", "subject")

    def __str__(self):
        return f"{self.name} ({self.subject.name})"

class Topic(models.Model):
    name = models.CharField(max_length=100)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="topics")

    class Meta:
        unique_together = ("name", "chapter")

    def __str__(self):
        return f"{self.name} ({self.chapter.name})"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name



class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice'),
        ('ImageMCQ', 'Image-Based Multiple Choice'),
    ]

    text = models.TextField()
    image = models.ImageField(upload_to='questions/images/', null=True, blank=True, help_text="Upload an image for ImageMCQ type.")
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, related_name="questions")
    subject = models.ForeignKey("Subject", on_delete=models.SET_NULL, null=True, related_name="questions")
    chapter = models.ForeignKey("Chapter", on_delete=models.SET_NULL, null=True, blank=True, related_name="questions")
    topic = models.ForeignKey("Topic", on_delete=models.SET_NULL, null=True, blank=True, related_name="questions")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="medium")
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="MCQ")

    # Specific fields for options
    option1 = models.CharField(max_length=255, blank=True, null=True, help_text="Option 1 for MCQ")
    option2 = models.CharField(max_length=255, blank=True, null=True, help_text="Option 2 for MCQ")
    option3 = models.CharField(max_length=255, blank=True, null=True, help_text="Option 3 for MCQ")
    option4 = models.CharField(max_length=255, blank=True, null=True, help_text="Option 4 for MCQ")

    correct_answer = models.CharField(
        max_length=10,
        choices=[("option1", "Option 1"), ("option2", "Option 2"), ("option3", "Option 3"), ("option4", "Option 4")],
        blank=True,
        null=True,
        help_text="Correct option for MCQ"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.question_type == "MCQ":
            if not all([self.option1, self.option2, self.option3, self.option4]):
                raise ValidationError("All 4 options must be provided for MCQ questions.")
            if self.correct_answer not in ["option1", "option2", "option3", "option4"]:
                raise ValidationError("Correct answer must match one of the 4 options.")
        elif self.question_type == "ImageMCQ":
            if not self.image:
                raise ValidationError("Image is mandatory for ImageMCQ type questions.")
            if not all([self.option1, self.option2, self.option3, self.option4]):
                raise ValidationError("All 4 options must be provided for ImageMCQ questions.")
            if self.correct_answer not in ["option1", "option2", "option3", "option4"]:
                raise ValidationError("Correct answer must match one of the 4 options.")
        super().clean()

    def __str__(self):
        return self.text

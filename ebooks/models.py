from django.db import models
from questions.models import Subject, Chapter, Topic

class Ebook(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='ebooks/pdf_files/', help_text="Upload the PDF file for the ebook.")
    cover_image = models.ImageField(upload_to='ebooks/cover_images/', help_text="Upload a cover image for the ebook.", null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="ebooks")
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name="ebooks")
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="ebooks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

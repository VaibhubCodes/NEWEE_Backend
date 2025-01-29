from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class PurchasedContent(models.Model):
    CONTENT_TYPES = [
        ('ebook', 'Ebook'),
        ('blog', 'Blog'),
        ('study_material', 'Study Material'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchased_content")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.PositiveIntegerField(help_text="ID of the purchased content")
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} purchased {self.content_type} ID: {self.content_id}"

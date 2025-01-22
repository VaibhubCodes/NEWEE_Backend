from rest_framework import serializers
from .models import Ebook

class EbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ebook
        fields = [
            'id', 'title', 'description', 'pdf_file', 'cover_image',
            'subject', 'chapter', 'topic', 'created_at', 'updated_at'
        ]

from rest_framework import serializers
from .models import PurchasedContent
from ebooks.models import Ebook
from blogs.models import Blog
from StudyMaterial.models import StudyMaterial


# Serializer for PurchasedContent Model
class PurchasedContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasedContent
        fields = ['id', 'user', 'content_type', 'content_id', 'purchase_date']


# Serializer for Ebook
class EbookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ebook
        fields = ['id', 'title', 'description', 'pdf_file', 'cover_image', 'is_premium', 'unlock_cost']


# Serializer for Blog
class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'main_image', 'is_premium', 'unlock_cost']


# Serializer for StudyMaterial
class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'description', 'is_premium', 'unlock_cost']

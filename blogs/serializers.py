from rest_framework import serializers
from .models import Blog, Comment, Tag, SavedBlog

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

class BlogSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'content', 'main_image', 'additional_images',
            'subject', 'chapter', 'topic', 'tags', 'author',
            'created_at', 'updated_at', 'view_count', 'comments'
        ]

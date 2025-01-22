from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Blog, Comment, SavedBlog
from .serializers import BlogSerializer, CommentSerializer

class BlogListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data)

class BlogDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, blog_id):
        blog = Blog.objects.get(id=blog_id)
        blog.view_count += 1
        blog.save()
        serializer = BlogSerializer(blog)
        return Response(serializer.data)

class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, blog_id):
        blog = Blog.objects.get(id=blog_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, blog=blog)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

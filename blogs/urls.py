from django.urls import path
from .views import BlogListView, BlogDetailView, CommentView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('blogs/', BlogListView.as_view(), name='blog-list'),
    path('blogs/<int:blog_id>/', BlogDetailView.as_view(), name='blog-detail'),
    path('blogs/<int:blog_id>/comment/', CommentView.as_view(), name='blog-comment'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

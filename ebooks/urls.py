from django.urls import path
from .views import EbookListView, EbookDetailView

urlpatterns = [
    path('ebooks/', EbookListView.as_view(), name='ebook-list'),
    path('ebooks/<int:ebook_id>/', EbookDetailView.as_view(), name='ebook-detail'),
]

from django.urls import path
from .views import (
    SubjectListView,
    ChapterListView,
    TopicListView,
    QuestionListView,
    BulkUploadQuestionsView,
    CategoryListView,
    RecentQuestionsView,FilteredQuestionsView
)

urlpatterns = [
    path("subjects/", SubjectListView.as_view(), name="subject-list"),
    path("chapters/", ChapterListView.as_view(), name="chapter-list"),
    path("topics/", TopicListView.as_view(), name="topic-list"),
    path("questions/", QuestionListView.as_view(), name="question-list"),
    path('questions/filter/', FilteredQuestionsView.as_view(), name='filtered-questions'),
    path("questions/recent/", RecentQuestionsView.as_view(), name="recent-questions"),  # New endpoint
    path("questions/bulk-upload/", BulkUploadQuestionsView.as_view(), name="bulk-upload-questions"),
    path("categories/", CategoryListView.as_view(), name="category-list"),  # Add this
]

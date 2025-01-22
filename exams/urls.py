from django.urls import path
from .views import ExamListView, ExamDetailView,SectionCreateView, SectionDetailView,AddSectionQuestionsView,SectionListView

urlpatterns = [
    path('exams/', ExamListView.as_view(), name='exam-list'),
    path('exams/<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),
    path('sections/create/', SectionCreateView.as_view(), name='section-create'),
    path('sections/', SectionListView.as_view(), name='section-list'),  # Add this line
    path('sections/<int:pk>/', SectionDetailView.as_view(), name='section-detail'),
    path('sections/<int:section_id>/add-questions/', AddSectionQuestionsView.as_view(), name='add-section-questions'),
]

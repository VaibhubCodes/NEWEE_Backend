from django.urls import path
from .views import AskQuestionView, BookMentorshipSessionView, AvailableSlotsView

urlpatterns = [
    path('available-slots/<int:teacher_id>/', AvailableSlotsView.as_view(), name='available-slots'),
    path('ask-question/', AskQuestionView.as_view(), name='ask-question'),
    path('book-session/', BookMentorshipSessionView.as_view(), name='book-session'),
]

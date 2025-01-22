from django.urls import path
from .views import StartQuizView, SubmitAnswerView,QuizStatusView, FinalizeQuizView, LeaderboardView, ParticipantResultView, ParticipantDetailsView

urlpatterns = [
    path('quizzes/<int:quiz_id>/start/', StartQuizView.as_view(), name='start-quiz'),
    path('participants/<int:participant_id>/submit/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('participants/<int:participant_id>/finalize/', FinalizeQuizView.as_view(), name='finalize-quiz'),
    path('quizzes/<int:quiz_id>/leaderboard/', LeaderboardView.as_view(), name='quiz-leaderboard'),
    path("quiz/<int:quiz_id>/status/", QuizStatusView.as_view(), name="quiz-status"),
    path('participants/<int:participant_id>/result/', ParticipantResultView.as_view(), name='participant-result'),
    path("participants/<int:participant_id>/details/", ParticipantDetailsView.as_view(), name="participant-details"),
]

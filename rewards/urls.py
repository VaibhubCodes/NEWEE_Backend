from django.urls import path
from .views import StartReadingBlogView,StreakSettlementView,ContestStreakProgressView, UpdateReadingActivityView, StopReadingBlogView, ContestStreakView, ContestStreakRewardListView

urlpatterns = [
    path('blogs/<int:blog_id>/start-reading/', StartReadingBlogView.as_view(), name='start-reading'),
    path('activity/<int:activity_id>/update-reading/', UpdateReadingActivityView.as_view(), name='update-reading'),
    path('activity/<int:activity_id>/stop-reading/', StopReadingBlogView.as_view(), name='stop-reading'),
    path('contests/streak/', ContestStreakView.as_view(), name='contest-streak'),
    path('contests/streak/rewards/', ContestStreakRewardListView.as_view(), name='contest-streak-rewards'),
    path('streak/settlement/', StreakSettlementView.as_view(), name='streak-settlement'),
    path('streak/progress/', ContestStreakProgressView.as_view(), name='streak-progress'),
]

from django.urls import path
from .views import ContestListView, CreateContestView, UpdateContestView, DeleteContestView, JoinContestView, DistributePrizesView

urlpatterns = [
    path("contests/", ContestListView.as_view(), name="contest-list"),
    path("contests/create/", CreateContestView.as_view(), name="create-contest"),
    path("contests/<int:contest_id>/update/", UpdateContestView.as_view(), name="update-contest"),
    path("contests/<int:contest_id>/delete/", DeleteContestView.as_view(), name="delete-contest"),
    path("contests/<int:contest_id>/join/", JoinContestView.as_view(), name="join-contest"),
    path("contests/<int:contest_id>/distribute-prizes/", DistributePrizesView.as_view(), name="distribute-prizes"),
]

from django.urls import path
from .views import (
    SendFriendRequestView,
    RespondToFriendRequestView,
    NearbyUsersView,
)

urlpatterns = [
    path('friend-request/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend-request/<int:request_id>/respond/', RespondToFriendRequestView.as_view(), name='respond-friend-request'),
    path('users/nearby/', NearbyUsersView.as_view(), name='nearby-users'),
]

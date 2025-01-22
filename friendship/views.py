from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FriendshipRequest, Friendship, find_nearby_users
from .serializers import FriendshipRequestSerializer, FriendshipSerializer
from users.models import CustomUser
from users.serializers import UserSerializer


class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        to_user_id = request.data.get("to_user")
        if not to_user_id:
            return Response({"error": "to_user ID is required."}, status=400)

        try:
            to_user = CustomUser.objects.get(id=to_user_id)
            if to_user == request.user:
                return Response({"error": "You cannot send a friend request to yourself."}, status=400)

            # Prevent sending friend request if already friends
            if Friendship.objects.filter(user=request.user, friend=to_user).exists():
                return Response({"error": "You are already friends."}, status=400)

            FriendshipRequest.objects.create(from_user=request.user, to_user=to_user)
            return Response({"message": "Friend request sent successfully."}, status=201)

        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=404)



class RespondToFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        action = request.data.get("action")  # Accept or Reject
        if action not in ['accept', 'reject']:
            return Response({"error": "Invalid action. Use 'accept' or 'reject'."}, status=400)

        try:
            friend_request = FriendshipRequest.objects.get(id=request_id, to_user=request.user)

            if action == 'accept':
                # Check if a friendship already exists
                existing_friendship = Friendship.objects.filter(
                    user=friend_request.from_user,
                    friend=friend_request.to_user
                ).exists()

                if not existing_friendship:
                    # Create mutual friendships
                    Friendship.objects.create(user=friend_request.from_user, friend=friend_request.to_user)
                    Friendship.objects.create(user=friend_request.to_user, friend=friend_request.from_user)

                # Update the status of the friend request
                friend_request.status = 'accepted'
                friend_request.save()
                return Response({"message": "Friend request accepted and mutual friendship established."}, status=200)

            elif action == 'reject':
                friend_request.status = 'rejected'
                friend_request.save()
                return Response({"message": "Friend request rejected."}, status=200)

        except FriendshipRequest.DoesNotExist:
            return Response({"error": "Friend request not found."}, status=404)



class NearbyUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")

        if not latitude or not longitude:
            return Response({"error": "Latitude and longitude are required."}, status=400)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return Response({"error": "Invalid latitude or longitude."}, status=400)

        nearby_users = find_nearby_users(latitude, longitude)
        serializer = UserSerializer(nearby_users, many=True)
        return Response(serializer.data, status=200)

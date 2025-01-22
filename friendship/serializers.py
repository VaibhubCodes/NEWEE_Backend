from rest_framework import serializers
from .models import FriendshipRequest, Friendship, NearbyUserSearch
from users.serializers import UserSerializer


class FriendshipRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer()

    class Meta:
        model = FriendshipRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at']


class FriendshipSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    friend = UserSerializer()

    class Meta:
        model = Friendship
        fields = ['id', 'user', 'friend', 'created_at']


class NearbyUserSearchSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = NearbyUserSearch
        fields = ['id', 'user', 'radius_km', 'searched_at']

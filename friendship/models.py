from django.db import models
from django.conf import settings
from geopy.distance import geodesic


class FriendshipRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"


class Friendship(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friends'
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friend_of'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')
        verbose_name = "Friendship"
        verbose_name_plural = "Friendships"

    def __str__(self):
        return f"{self.user} is friends with {self.friend}"


class NearbyUserSearch(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='searches'
    )
    radius_km = models.DecimalField(max_digits=5, decimal_places=2)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Search by {self.user} ({self.radius_km} km)"


def find_nearby_users(latitude, longitude, distance_km=30):
    users = settings.AUTH_USER_MODEL.objects.exclude(latitude__isnull=True, longitude__isnull=True)
    nearby_users = []

    for user in users:
        user_coords = (user.latitude, user.longitude)
        current_coords = (latitude, longitude)
        if geodesic(current_coords, user_coords).km <= distance_km:
            nearby_users.append(user)

    return nearby_users

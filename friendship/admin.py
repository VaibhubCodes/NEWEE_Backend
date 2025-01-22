from django.contrib import admin
from .models import FriendshipRequest, Friendship, NearbyUserSearch


@admin.register(FriendshipRequest)
class FriendshipRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('from_user__username', 'to_user__username')


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at')
    search_fields = ('user__username', 'friend__username')


@admin.register(NearbyUserSearch)
class NearbyUserSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'radius_km', 'searched_at')

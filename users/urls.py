from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    ProfileView,
    UserListView,
    ProfileUpdateView,
    StudentFilterView,
    UpdateLocationView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('students/filter/', StudentFilterView.as_view(), name='student-filter'),
    path('location/update/', UpdateLocationView.as_view(), name='update-location'),
]

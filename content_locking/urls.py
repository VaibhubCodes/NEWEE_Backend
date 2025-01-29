from django.urls import path
from .views import UnlockContentView

urlpatterns = [
    path('unlock-content/', UnlockContentView.as_view(), name='unlock-content'),
]

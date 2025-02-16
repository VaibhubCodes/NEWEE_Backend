from django.urls import path
from .views import UploadPDFView,GetQuizView

urlpatterns = [
    path('upload-pdf/', UploadPDFView.as_view(), name='upload-pdf'),
    path('quiz/<int:pk>/', GetQuizView.as_view(), name='get-quiz'), 
]

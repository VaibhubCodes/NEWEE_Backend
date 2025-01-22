from django.urls import path
from .views import StudyMaterialListView, StudyMaterialDetailView, EnrollView

urlpatterns = [
    path('study-materials/', StudyMaterialListView.as_view(), name='study-material-list'),
    path('study-materials/<int:material_id>/', StudyMaterialDetailView.as_view(), name='study-material-detail'),
    path('study-materials/<int:material_id>/enroll/', EnrollView.as_view(), name='enroll'),
]

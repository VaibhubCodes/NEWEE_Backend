from django.urls import path
from .views import SectionListView,QuizTypesView, AddQuestionsToSectionView, QuizListView,SectionQuestionsView,UpdateSectionQuestionsView,QuizDetailView,QuizSectionsView,CreateQuizView

urlpatterns = [
    path('sections/', SectionListView.as_view(), name='section-list'),
    path('sections/<int:section_id>/questions/', SectionQuestionsView.as_view(), name='section-questions'),
    path('sections/<int:section_id>/add-questions/', AddQuestionsToSectionView.as_view(), name='add-questions-to-section'),
    path('sections/<int:section_id>/update-questions/', UpdateSectionQuestionsView.as_view(), name='update-questions'),
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),
    path('quiz-types/', QuizTypesView.as_view(), name='quiz-types'),
    path('quizzes/create/', CreateQuizView.as_view(), name='create-quiz'),
    path('quizzes/<int:quiz_id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:quiz_id>/sections/', QuizSectionsView.as_view(), name='section-list'),
    
]

from django.urls import path
from leaderboard_service.views import CreateUserView, CreateGameView, ScoreIngestionView

urlpatterns = [
    path('api/v1/create-user/',
         CreateUserView.as_view(), name='create-user'),
    path('api/v1/create-game/',
         CreateGameView.as_view(), name='create-game'),
    path('api/v1/score-ingestion/',
         ScoreIngestionView.as_view(),name='score-ingestion-view')
]

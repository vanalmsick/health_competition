"""
URL configuration for health_competition project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from competition.views import CompetitionViewSet, TeamViewSet, ActivityGoalViewSet, PointsViewSet, CompetitionStatsQueryView, FeedQueryView, JoinCompetitionView, JoinTeamView
from workouts.views import WorkoutViewSet
from custom_user.views import CustomUserViewSet, LinkStravaView, UnlinkStravaView

router = DefaultRouter()
router.register(r'competition', CompetitionViewSet, basename='competition')
router.register(r'team', TeamViewSet, basename='teams')
router.register(r'goal', ActivityGoalViewSet, basename='goal')
router.register(r'workout', WorkoutViewSet, basename='workout')
router.register(r'point', PointsViewSet, basename='points')
router.register(r'user', CustomUserViewSet, basename='cutomuser')

urlpatterns = [
    path('api/', include([
        path('', include(router.urls)),
        path('stats/<int:competition>/', CompetitionStatsQueryView.as_view(), name='competition-stats'),
        path('feed/<int:competition>/', FeedQueryView.as_view(), name='competition-feed'),
        path('join/competition/<str:join_code>/', JoinCompetitionView.as_view(), name='join-competition'),
        path('join/team/<int:id>/', JoinTeamView.as_view(), name='join-team'),
        path('strava/link/<str:code>/', LinkStravaView.as_view(), name='link-strava'),
        path('strava/unlink/', UnlinkStravaView.as_view(), name='unlink-strava'),
        path('token/', TokenObtainPairView.as_view(), name='token-initial'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    ])),
    path('admin/', admin.site.urls),
]


admin.site.site_header = 'Backend Admin Panel'
admin.site.site_title = 'Health Competition Backend'
admin.site.index_title = 'Welcome to the Health Competition Backend'

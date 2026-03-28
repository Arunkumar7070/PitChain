from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet, IPLTeamViewSet

router = DefaultRouter()
router.register('teams', IPLTeamViewSet)
router.register('', PlayerViewSet)

urlpatterns = [path('', include(router.urls))]

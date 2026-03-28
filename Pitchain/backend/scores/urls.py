from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerScoreViewSet

router = DefaultRouter()
router.register('', PlayerScoreViewSet)

urlpatterns = [path('', include(router.urls))]

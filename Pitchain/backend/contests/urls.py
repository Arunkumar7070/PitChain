from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContestViewSet, UserEntryCreateView

router = DefaultRouter()
router.register('', ContestViewSet)

urlpatterns = [
    path('entries/', UserEntryCreateView.as_view(), name='create-entry'),
    path('', include(router.urls)),
]

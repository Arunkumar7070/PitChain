from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import PlayerScore
from .serializers import PlayerScoreSerializer


class PlayerScoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlayerScore.objects.select_related('player', 'contest')
    serializer_class = PlayerScoreSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['contest', 'player']

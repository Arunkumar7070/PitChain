from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Player, IPLTeam
from .serializers import PlayerSerializer, IPLTeamSerializer


class IPLTeamViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IPLTeam.objects.all()
    serializer_class = IPLTeamSerializer
    permission_classes = [AllowAny]


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.select_related('team').filter(is_playing=True)
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['team', 'role']
    search_fields = ['name']

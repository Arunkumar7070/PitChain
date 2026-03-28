from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Contest, UserEntry
from .serializers import ContestSerializer, UserEntrySerializer


class ContestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contest.objects.all().order_by('-match__match_date')
    serializer_class = ContestSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['status']

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def my_entry(self, request, pk=None):
        """Get the current user's entry for this contest."""
        contest = self.get_object()
        try:
            entry = UserEntry.objects.get(user=request.user, contest=contest)
            return Response(UserEntrySerializer(entry).data)
        except UserEntry.DoesNotExist:
            return Response({'detail': 'No entry found.'}, status=status.HTTP_404_NOT_FOUND)


class UserEntryCreateView(generics.CreateAPIView):
    """POST /api/contests/entries/ — Submit team + record tx hash"""
    serializer_class = UserEntrySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

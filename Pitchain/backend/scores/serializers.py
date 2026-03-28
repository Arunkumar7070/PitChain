from rest_framework import serializers
from .models import PlayerScore


class PlayerScoreSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.name', read_only=True)

    class Meta:
        model = PlayerScore
        fields = '__all__'

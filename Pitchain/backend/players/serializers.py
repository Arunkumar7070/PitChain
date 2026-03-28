from rest_framework import serializers
from .models import Player, IPLTeam


class IPLTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPLTeam
        fields = '__all__'


class PlayerSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.short_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'name', 'team', 'team_name', 'role', 'role_display',
                  'credit_value', 'is_playing', 'image_url']

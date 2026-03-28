from rest_framework import serializers
from .models import Contest, UserEntry


class ContestSerializer(serializers.ModelSerializer):
    participant_count = serializers.ReadOnlyField()
    match_name  = serializers.CharField(source='match.match_name', read_only=True)
    team_a      = serializers.CharField(source='match.team_a', read_only=True)
    team_b      = serializers.CharField(source='match.team_b', read_only=True)
    match_date  = serializers.DateTimeField(source='match.match_date', read_only=True)

    class Meta:
        model = Contest
        fields = ['id', 'name', 'match_name', 'team_a', 'team_b', 'match_date',
                  'entry_fee_eth', 'prize_pool_eth', 'max_participants',
                  'participant_count', 'status']


class UserEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEntry
        fields = ['id', 'contest', 'selected_players', 'captain_id',
                  'vice_captain_id', 'total_points', 'rank', 'tx_hash', 'prize_claimed']
        read_only_fields = ['total_points', 'rank', 'prize_claimed']

    def validate_selected_players(self, value):
        if len(value) != 11:
            raise serializers.ValidationError('You must select exactly 11 players.')
        return value

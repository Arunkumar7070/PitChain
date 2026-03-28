from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    win_rate = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'wallet_address', 'total_winnings',
                  'contests_played', 'contests_won', 'win_rate', 'created_at']
        read_only_fields = ['total_winnings', 'contests_played', 'contests_won', 'created_at']


class WalletAuthSerializer(serializers.Serializer):
    """Used for MetaMask wallet-based login."""
    wallet_address = serializers.CharField(max_length=42)
    signature = serializers.CharField()
    message = serializers.CharField()

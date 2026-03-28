from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extended user model for Pitchain.
    Wallet address is the primary Web3 identifier.
    """
    wallet_address = models.CharField(max_length=42, unique=True, null=True, blank=True)
    total_winnings = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    contests_played = models.PositiveIntegerField(default=0)
    contests_won = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.wallet_address or self.username

    @property
    def win_rate(self):
        if self.contests_played == 0:
            return 0
        return round((self.contests_won / self.contests_played) * 100, 2)

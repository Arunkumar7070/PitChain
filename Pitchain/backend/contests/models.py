from django.db import models
from django.conf import settings


class Contest(models.Model):
    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('LIVE', 'Live'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    match_name = models.CharField(max_length=200)          # e.g. "MI vs CSK"
    team_a = models.CharField(max_length=100)
    team_b = models.CharField(max_length=100)
    match_date = models.DateTimeField()
    entry_fee_eth = models.DecimalField(max_digits=18, decimal_places=8)  # ETH amount
    prize_pool_eth = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    max_participants = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING')

    # On-chain tracking
    contract_contest_id = models.PositiveIntegerField(null=True, blank=True)
    tx_hash_created = models.CharField(max_length=66, blank=True)  # Creation tx

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contests'

    def __str__(self):
        return f"{self.match_name} — {self.name}"

    @property
    def participant_count(self):
        return self.entries.count()


class UserEntry(models.Model):
    """A user's team submission for a contest."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='entries')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='entries')
    selected_players = models.JSONField()     # List of 11 player IDs
    captain_id = models.IntegerField()        # Captain (2x points)
    vice_captain_id = models.IntegerField()   # Vice-captain (1.5x points)
    total_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)

    # On-chain entry proof
    tx_hash = models.CharField(max_length=66, blank=True)  # Entry payment tx
    prize_claimed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_entries'
        unique_together = ['user', 'contest']   # One team per contest per user

    def __str__(self):
        return f"{self.user} → {self.contest}"

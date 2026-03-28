"""
contests/models.py
Day 2: Match, Contest (with chain config), PrizeDistribution, AdminEarnings
"""
import logging
from decimal import Decimal
from django.db import models # type: ignore
from django.conf import settings # type: ignore

logger = logging.getLogger('pitchain')

print("[contests] Loading contests models...")

# ─── Constants ────────────────────────────────────────────────────────────────
NETWORK_BASE_SEPOLIA  = 'base-sepolia'
CHAIN_ID_BASE_SEPOLIA = 84532
DEFAULT_ENTRY_FEE_ETH = Decimal('0.003')   # 0.003 ETH per contest entry
PLATFORM_FEE_PERCENT  = Decimal('5.0')     # 5% admin cut from prize pool


# ─── Match ────────────────────────────────────────────────────────────────────

class Match(models.Model):
    """A real IPL cricket match (the anchor for all contests)."""

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE',      'Live'),
        ('COMPLETED', 'Completed'),
        ('ABANDONED', 'Abandoned'),
    ]

    team_a      = models.CharField(max_length=100, help_text="Home team short name e.g. MI")
    team_b      = models.CharField(max_length=100, help_text="Away team short name e.g. CSK")
    venue       = models.CharField(max_length=200, blank=True)
    match_date  = models.DateTimeField()
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SCHEDULED')
    external_id = models.CharField(max_length=100, blank=True, unique=True,
                                   help_text="ID from cricket data API (Cricbuzz / RapidAPI)")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matches'
        ordering = ['-match_date']
        indexes  = [
            models.Index(fields=['status'],     name='idx_matches_status'),
            models.Index(fields=['match_date'], name='idx_matches_date'),
        ]

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} | {self.match_date.strftime('%d %b %Y')}"

    @property
    def match_name(self):
        return f"{self.team_a} vs {self.team_b}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            print(f"[contests] 📅 New match created: {self.match_name} on {self.match_date.strftime('%d %b %Y %H:%M')}")
            logger.info(f"Match created | id={self.pk} | {self.match_name}")


# ─── Contest ──────────────────────────────────────────────────────────────────

class Contest(models.Model):
    """
    A fantasy contest tied to a Match.
    Runs on Base Sepolia testnet — chain_id=84532.
    Default entry fee = 0.003 ETH.
    """

    STATUS_CHOICES = [
        ('UPCOMING',   'Upcoming'),
        ('LIVE',       'Live'),
        ('COMPLETED',  'Completed'),
        ('CANCELLED',  'Cancelled'),
    ]

    # ── Core ─────────────────────────────────────────────────────────
    name             = models.CharField(max_length=200)
    match            = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='contests')
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UPCOMING')
    max_participants = models.PositiveIntegerField(default=100)

    # ── Entry & Prize ─────────────────────────────────────────────────
    entry_fee_eth  = models.DecimalField(max_digits=18, decimal_places=8,
                                         default=DEFAULT_ENTRY_FEE_ETH,
                                         help_text="Entry fee in ETH (default 0.003)")
    prize_pool_eth = models.DecimalField(max_digits=18, decimal_places=8, default=0,
                                         help_text="Accumulated from entries (auto-updated)")

    # ── Blockchain / Web3 ────────────────────────────────────────────
    network              = models.CharField(max_length=50, default=NETWORK_BASE_SEPOLIA,
                                            help_text="Blockchain network identifier")
    chain_id             = models.PositiveIntegerField(default=CHAIN_ID_BASE_SEPOLIA,
                                                       help_text="EVM chain ID (Base Sepolia = 84532)")
    contract_contest_id  = models.PositiveIntegerField(null=True, blank=True,
                                                        help_text="Solidity contest ID on-chain")
    tx_hash_created      = models.CharField(max_length=66, blank=True,
                                             help_text="Tx hash from createContest() call")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contests'
        indexes  = [
            models.Index(fields=['status'],              name='idx_contests_status'),
            models.Index(fields=['match', 'status'],     name='idx_contests_match_status'),
            models.Index(fields=['contract_contest_id'], name='idx_contests_contract_id'),
        ]

    def __str__(self):
        return f"[{self.status}] {self.name} | {self.match.match_name}"

    @property
    def participant_count(self):
        return self.user_teams.count()

    @property
    def is_full(self):
        return self.participant_count >= self.max_participants

    @property
    def platform_fee_eth(self):
        return (self.prize_pool_eth * PLATFORM_FEE_PERCENT / 100).quantize(Decimal('0.00000001'))

    @property
    def net_prize_pool_eth(self):
        return self.prize_pool_eth - self.platform_fee_eth

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            print(
                f"[contests] 🏆 New contest: '{self.name}' | "
                f"match={self.match.match_name} | "
                f"fee={self.entry_fee_eth} ETH | "
                f"network={self.network} | chain_id={self.chain_id}"
            )
            logger.info(
                f"Contest created | id={self.pk} | name={self.name} | "
                f"entry_fee={self.entry_fee_eth} | chain_id={self.chain_id}"
            )


# ─── UserEntry ────────────────────────────────────────────────────────────────

class UserEntry(models.Model):
    """
    A user's team submission for a contest.
    Records the 11 selected players, captain, tx hash, and scoring outcome.
    """

    contest          = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='user_teams')
    user             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                         related_name='contest_entries')
    selected_players = models.JSONField(help_text="List of 11 player IDs selected by the user")
    captain_id       = models.PositiveIntegerField(help_text="Player ID designated as captain")
    vice_captain_id  = models.PositiveIntegerField(help_text="Player ID designated as vice-captain")
    total_points     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rank             = models.PositiveIntegerField(null=True, blank=True)
    tx_hash          = models.CharField(max_length=66, blank=True,
                                        help_text="On-chain tx hash for the entry fee payment")
    prize_claimed    = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'user_entries'
        unique_together = [('contest', 'user')]
        indexes         = [
            models.Index(fields=['contest', 'user'], name='idx_entries_contest_user'),
            models.Index(fields=['contest', 'rank'], name='idx_entries_contest_rank'),
        ]

    def __str__(self):
        return f"Entry | user={self.user} | contest={self.contest_id} | pts={self.total_points}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"UserEntry created | user={self.user_id} | contest={self.contest_id} | tx={self.tx_hash}")


# ─── PrizeDistribution ────────────────────────────────────────────────────────

class PrizeDistribution(models.Model):
    """
    Records each winner's prize payout for a contest.
    One row per winner (top-3 or custom payout structure).
    """

    contest    = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='prize_distributions')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='prizes_won')
    rank       = models.PositiveIntegerField(help_text="1 = winner, 2 = runner-up, etc.")
    prize_eth  = models.DecimalField(max_digits=18, decimal_places=8,
                                     help_text="ETH amount distributed to this user")
    tx_hash    = models.CharField(max_length=66, blank=True,
                                  help_text="On-chain tx hash for the prize transfer")
    distributed_at = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table       = 'prize_distributions'
        unique_together = [('contest', 'rank')]
        ordering        = ['rank']
        verbose_name    = 'Prize Distribution'

    def __str__(self):
        return f"Rank #{self.rank} | {self.user} | {self.prize_eth} ETH"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            print(
                f"[contests] 💰 Prize recorded | contest={self.contest_id} | "
                f"rank=#{self.rank} | user={self.user} | {self.prize_eth} ETH | "
                f"tx={self.tx_hash[:10] + '...' if self.tx_hash else 'PENDING'}"
            )
            logger.info(f"PrizeDistribution | contest={self.contest_id} | rank={self.rank} | eth={self.prize_eth}")


# ─── AdminEarnings ────────────────────────────────────────────────────────────

class AdminEarnings(models.Model):
    """
    Platform fee collected per contest (5% of prize pool by default).
    Transferred to the deployer/owner wallet on-chain.
    """

    contest        = models.OneToOneField(Contest, on_delete=models.CASCADE,
                                          related_name='admin_earnings')
    amount_eth     = models.DecimalField(max_digits=18, decimal_places=8,
                                         help_text="ETH collected as platform fee")
    percentage     = models.DecimalField(max_digits=5, decimal_places=2,
                                         default=PLATFORM_FEE_PERCENT,
                                         help_text="Fee % taken (default 5.0)")
    tx_hash        = models.CharField(max_length=66, blank=True,
                                      help_text="On-chain tx hash for fee transfer to owner")
    recipient_wallet = models.CharField(max_length=42, blank=True,
                                         help_text="Owner wallet that received the fee")
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table     = 'admin_earnings'
        verbose_name = 'Admin Earnings'

    def __str__(self):
        return f"AdminEarnings | contest={self.contest_id} | {self.amount_eth} ETH ({self.percentage}%)"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            print(
                f"[contests] 🏦 Admin fee recorded | contest={self.contest_id} | "
                f"{self.amount_eth} ETH ({self.percentage}%) → {self.recipient_wallet or 'wallet TBD'}"
            )
            logger.info(f"AdminEarnings | contest={self.contest_id} | amount={self.amount_eth}")

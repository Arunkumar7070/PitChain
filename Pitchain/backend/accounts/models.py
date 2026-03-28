"""
accounts/models.py
Day 2: Custom User model with wallet_address as Web3 identity.
"""
import logging
from django.contrib.auth.models import AbstractUser
from django.db import models

logger = logging.getLogger('pitchain')


class User(AbstractUser):
    """
    Pitchain User.
    - wallet_address : MetaMask address (primary Web3 identity)
    - is_admin       : platform admin flag (separate from Django is_staff)
    """

    wallet_address = models.CharField(
        max_length=42,
        unique=True,
        null=True,
        blank=True,
        help_text="MetaMask wallet address (0x...)",
    )
    is_admin = models.BooleanField(
        default=False,
        help_text="True if this user is a Pitchain platform admin",
    )
    total_winnings = models.DecimalField(
        max_digits=18, decimal_places=8, default=0,
        help_text="Cumulative ETH winnings across all contests",
    )
    contests_played = models.PositiveIntegerField(default=0)
    contests_won    = models.PositiveIntegerField(default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table       = 'users'
        verbose_name   = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['wallet_address'], name='idx_users_wallet'),
        ]

    def __str__(self):
        return self.wallet_address or self.username

    # ── computed properties ──────────────────────────────────────────
    @property
    def win_rate(self):
        if self.contests_played == 0:
            return 0.0
        return round((self.contests_won / self.contests_played) * 100, 2)

    @property
    def short_wallet(self):
        """Returns 0x1234...abcd format."""
        if self.wallet_address:
            return f"{self.wallet_address[:6]}...{self.wallet_address[-4:]}"
        return "—"

    # ── save hook with logging ───────────────────────────────────────
    def save(self, *args, **kwargs):
        # Normalise wallet address to lowercase (EIP-55 checksums vary)
        if self.wallet_address:
            self.wallet_address = self.wallet_address.lower()

        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            print(f"[accounts] 🆕 New user created | wallet={self.short_wallet} | is_admin={self.is_admin}")
            logger.info(f"New user registered | id={self.pk} | wallet={self.short_wallet}")
        else:
            print(f"[accounts] ✏️  User updated    | wallet={self.short_wallet}")
            logger.debug(f"User updated | id={self.pk}")

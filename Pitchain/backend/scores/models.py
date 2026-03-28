"""
scores/models.py
Day 2: UserTeam (contest entry) + UserTeamPlayer (11-player selection)
"""
import logging
from django.db import models
from django.conf import settings

logger = logging.getLogger('pitchain')

print("[scores] Loading scores models...")


# ─── PlayerScore ──────────────────────────────────────────────────────────────

class PlayerScore(models.Model):
    """
    Real match performance stats for a player in a contest.
    Used to calculate fantasy points after match completes.
    """

    player  = models.ForeignKey('players.Player', on_delete=models.CASCADE,
                                 related_name='scores')
    contest = models.ForeignKey('contests.Contest', on_delete=models.CASCADE,
                                 related_name='player_scores')

    # ── Batting ───────────────────────────────────────────────────────
    runs         = models.PositiveIntegerField(default=0)
    balls_faced  = models.PositiveIntegerField(default=0)
    fours        = models.PositiveIntegerField(default=0)
    sixes        = models.PositiveIntegerField(default=0)

    # ── Bowling ───────────────────────────────────────────────────────
    wickets      = models.PositiveIntegerField(default=0)
    overs        = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    # ── Fielding ──────────────────────────────────────────────────────
    catches      = models.PositiveIntegerField(default=0)
    stumpings    = models.PositiveIntegerField(default=0)

    # ── Fantasy ───────────────────────────────────────────────────────
    fantasy_points = models.DecimalField(max_digits=8, decimal_places=2, default=0,
                                          help_text="Calculated fantasy points for this performance")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'player_scores'
        unique_together = [('player', 'contest')]
        indexes         = [
            models.Index(fields=['contest', 'fantasy_points'], name='idx_scores_contest_pts'),
        ]

    def __str__(self):
        return f"{self.player} | contest={self.contest_id} | {self.fantasy_points}pts"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"PlayerScore created | player={self.player_id} | contest={self.contest_id}")


# ─── UserTeam ─────────────────────────────────────────────────────────────────

class UserTeam(models.Model):
    """
    A user's fantasy team entry for one contest.
    One team per user per contest (enforced by unique_together).
    Linked on-chain via tx_hash (entry payment proof).
    """

    user    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_teams',
    )
    contest = models.ForeignKey(
        'contests.Contest',
        on_delete=models.CASCADE,
        related_name='score_user_teams',
    )

    # ── Points & Ranking ──────────────────────────────────────────────
    total_points = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Sum of selected players' fantasy points (captain 2x, vc 1.5x)",
    )
    rank = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Final leaderboard rank within this contest",
    )

    # ── On-chain proof ────────────────────────────────────────────────
    tx_hash = models.CharField(
        max_length=66, blank=True,
        help_text="Tx hash of the joinContest() call on Base Sepolia",
    )
    prize_claimed = models.BooleanField(
        default=False,
        help_text="True once prize ETH has been transferred on-chain",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'user_teams'
        unique_together = [('user', 'contest')]   # One team per contest per user
        ordering        = ['-total_points']
        indexes = [
            models.Index(fields=['contest', 'total_points'], name='idx_userteam_leaderboard'),
            models.Index(fields=['tx_hash'],                  name='idx_userteam_txhash'),
        ]

    def __str__(self):
        return f"{self.user} → {self.contest.name} | {self.total_points}pts | rank #{self.rank}"

    @property
    def captain(self):
        return self.players.filter(is_captain=True).first()

    @property
    def vice_captain(self):
        return self.players.filter(is_vice_captain=True).first()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            print(
                f"[scores] 📝 New team entry | user={self.user} | "
                f"contest={self.contest.name} | tx={self.tx_hash[:10] + '...' if self.tx_hash else 'PENDING'}"
            )
            logger.info(f"UserTeam created | id={self.pk} | user={self.user} | contest={self.contest_id}")


# ─── UserTeamPlayer ───────────────────────────────────────────────────────────

class UserTeamPlayer(models.Model):
    """
    One player slot in a UserTeam (11 rows per team).
    Captain earns 2× points, Vice-Captain earns 1.5×.
    points_earned is calculated after match ends.
    """

    user_team = models.ForeignKey(
        UserTeam,
        on_delete=models.CASCADE,
        related_name='players',
    )
    player = models.ForeignKey(
        'players.Player',
        on_delete=models.CASCADE,
        related_name='team_selections',
    )
    is_captain      = models.BooleanField(default=False)
    is_vice_captain = models.BooleanField(default=False)

    # Filled after match completes
    points_earned = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        help_text="Base fantasy points × multiplier (2x captain / 1.5x vc)",
    )

    class Meta:
        db_table        = 'user_team_players'
        unique_together = [('user_team', 'player')]   # A player can only appear once per team
        indexes = [
            models.Index(fields=['user_team'], name='idx_utplayer_team'),
            models.Index(fields=['player'],    name='idx_utplayer_player'),
        ]

    def __str__(self):
        role = "©" if self.is_captain else ("vc" if self.is_vice_captain else "  ")
        return f"[{role}] {self.player.name} → {self.points_earned}pts"

    @property
    def multiplier(self):
        """Returns the points multiplier for this slot."""
        if self.is_captain:      return 2.0
        if self.is_vice_captain: return 1.5
        return 1.0

    def apply_multiplier(self, base_points):
        """Calculate and store final points for this player slot."""
        self.points_earned = round(base_points * self.multiplier, 2)
        print(
            f"[scores] {'👑' if self.is_captain else ('🥈' if self.is_vice_captain else '  ')} "
            f"{self.player.name} | base={base_points} × {self.multiplier} = {self.points_earned}pts"
        )
        logger.debug(
            f"Points applied | player={self.player.name} | "
            f"base={base_points} | multiplier={self.multiplier} | final={self.points_earned}"
        )
        return self.points_earned

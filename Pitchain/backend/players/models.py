"""
players/models.py
Day 2: IPLTeam, Player, PlayerMatchStats
"""
import logging
from django.db import models

logger = logging.getLogger('pitchain')

print("[players] Loading players models...")


# ─── IPL Team ────────────────────────────────────────────────────────────────

class IPLTeam(models.Model):
    """Represents one of the 10 IPL franchises."""

    name       = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10, unique=True)   # e.g. "MI", "CSK"
    logo_url   = models.URLField(blank=True)
    home_city  = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table     = 'ipl_teams'
        ordering     = ['name']
        verbose_name = 'IPL Team'
        verbose_name_plural = 'IPL Teams'

    def __str__(self):
        return f"{self.short_name} — {self.name}"

    def save(self, *args, **kwargs):
        self.short_name = self.short_name.upper()
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            print(f"[players] 🏟️  New team added: {self.short_name} ({self.name})")
            logger.info(f"IPLTeam created | id={self.pk} | short_name={self.short_name}")


# ─── Player ───────────────────────────────────────────────────────────────────

class Player(models.Model):
    """An IPL player available for fantasy team selection."""

    ROLE_CHOICES = [
        ('BAT', 'Batsman'),
        ('BWL', 'Bowler'),
        ('AR',  'All-Rounder'),
        ('WK',  'Wicket-Keeper'),
    ]

    name         = models.CharField(max_length=100)
    team         = models.ForeignKey(IPLTeam, on_delete=models.CASCADE, related_name='players')
    role         = models.CharField(max_length=3, choices=ROLE_CHOICES)
    credit_value = models.DecimalField(max_digits=4, decimal_places=1, default=8.0,
                                       help_text="Fantasy credit cost (e.g. 9.5)")
    is_playing   = models.BooleanField(default=True,
                                       help_text="True if in playing XI for current match")
    image_url    = models.URLField(blank=True)
    ipl_id       = models.CharField(max_length=50, unique=True, blank=True,
                                    help_text="External cricket API player ID")
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'players'
        indexes  = [
            models.Index(fields=['team', 'role'],   name='idx_players_team_role'),
            models.Index(fields=['is_playing'],      name='idx_players_playing'),
        ]

    def __str__(self):
        return f"{self.name} ({self.team.short_name} | {self.get_role_display()})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            print(f"[players] 🏏  New player: {self.name} | {self.team.short_name} | {self.get_role_display()} | ₹{self.credit_value}cr")
            logger.info(f"Player created | id={self.pk} | name={self.name} | team={self.team.short_name}")


# ─── PlayerMatchStats ─────────────────────────────────────────────────────────

class PlayerMatchStats(models.Model):
    """
    Real on-field statistics for one player in one match.
    Fetched from cricket API and used to calculate fantasy points.
    Unique per (player, match).
    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='match_stats')
    match  = models.ForeignKey('contests.Match', on_delete=models.CASCADE, related_name='player_stats')

    # ── Batting ──────────────────────────────────────────────────────
    runs        = models.IntegerField(default=0)
    balls_faced = models.IntegerField(default=0)
    fours       = models.IntegerField(default=0)
    sixes       = models.IntegerField(default=0)
    is_out      = models.BooleanField(default=False)   # duck penalty if runs==0

    # ── Bowling ──────────────────────────────────────────────────────
    overs_bowled  = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    wickets       = models.IntegerField(default=0)
    runs_conceded = models.IntegerField(default=0)
    maidens       = models.IntegerField(default=0)
    no_balls      = models.IntegerField(default=0)
    wides         = models.IntegerField(default=0)

    # ── Fielding ─────────────────────────────────────────────────────
    catches   = models.IntegerField(default=0)
    stumpings = models.IntegerField(default=0)
    run_outs  = models.IntegerField(default=0)

    # ── Computed fantasy points (saved after calculation) ─────────────
    fantasy_points = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table       = 'player_match_stats'
        unique_together = [('player', 'match')]
        verbose_name   = 'Player Match Stats'

    def __str__(self):
        return f"{self.player.name} @ Match#{self.match_id} → {self.fantasy_points}pts"

    # ─── Fantasy Point Engine ─────────────────────────────────────────
    def calculate_fantasy_points(self):
        """
        Dream11-style fantasy scoring.
        Called by the score update task after match data is fetched.
        """
        pts = 0

        # Played in the match at all (+4 if part of playing XI)
        played = (self.runs > 0 or self.balls_faced > 0 or
                  self.wickets > 0 or self.catches > 0 or
                  self.stumpings > 0 or self.overs_bowled > 0)
        if played:
            pts += 4

        # ── Batting ──────────────────────────────────────────────────
        pts += self.runs * 1
        pts += self.fours * 1
        pts += self.sixes * 2

        if self.runs >= 100:
            pts += 16
            print(f"[scores] 💯 CENTURY bonus for {self.player.name}! (+16)")
        elif self.runs >= 50:
            pts += 8
            print(f"[scores] ⚡ HALF-CENTURY bonus for {self.player.name}! (+8)")
        elif self.runs >= 30:
            pts += 4

        if self.runs == 0 and self.is_out:
            pts -= 2
            print(f"[scores] 🦆 DUCK penalty for {self.player.name} (-2)")

        # Strike-rate bonus (min 10 balls faced)
        if self.balls_faced >= 10:
            sr = (self.runs / self.balls_faced) * 100
            if sr > 170:   pts += 6
            elif sr > 150: pts += 4
            elif sr > 130: pts += 2

        # ── Bowling ──────────────────────────────────────────────────
        pts += self.wickets * 25
        pts += self.maidens * 4

        if self.wickets >= 5:
            pts += 16
            print(f"[scores] 🔥 5-WICKET haul bonus for {self.player.name}! (+16)")
        elif self.wickets >= 4:
            pts += 8
        elif self.wickets >= 3:
            pts += 4

        # Economy-rate bonus (min 2 overs)
        if float(self.overs_bowled) >= 2 and self.runs_conceded > 0:
            economy = self.runs_conceded / float(self.overs_bowled)
            if economy < 5:    pts += 6
            elif economy < 6:  pts += 4
            elif economy < 7:  pts += 2
            elif economy > 10: pts -= 2

        # ── Fielding ─────────────────────────────────────────────────
        pts += self.catches   * 8
        pts += self.stumpings * 12
        pts += self.run_outs  * 6

        self.fantasy_points = pts
        print(f"[scores] 📊 {self.player.name} → {pts} fantasy pts")
        logger.info(f"Fantasy points calculated | player={self.player.name} | pts={pts}")
        return pts

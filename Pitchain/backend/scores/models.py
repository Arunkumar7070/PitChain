from django.db import models
from players.models import Player
from contests.models import Contest


class PlayerScore(models.Model):
    """Real match scores fetched from cricket API and used for fantasy points."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scores')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='player_scores')

    # Batting
    runs = models.IntegerField(default=0)
    balls_faced = models.IntegerField(default=0)
    fours = models.IntegerField(default=0)
    sixes = models.IntegerField(default=0)
    is_dismissed = models.BooleanField(default=False)

    # Bowling
    overs = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    wickets = models.IntegerField(default=0)
    runs_conceded = models.IntegerField(default=0)
    maidens = models.IntegerField(default=0)

    # Fielding
    catches = models.IntegerField(default=0)
    stumpings = models.IntegerField(default=0)
    run_outs = models.IntegerField(default=0)

    # Computed
    fantasy_points = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'player_scores'
        unique_together = ['player', 'contest']

    def calculate_fantasy_points(self):
        """Standard Dream11-style fantasy point calculation."""
        pts = 0
        # Batting
        pts += self.runs * 1
        pts += self.fours * 1
        pts += self.sixes * 2
        if self.runs >= 100: pts += 16
        elif self.runs >= 50: pts += 8
        elif self.runs >= 30: pts += 4
        if self.runs == 0 and self.is_dismissed: pts -= 2
        # Strike rate bonus (min 10 balls)
        if self.balls_faced >= 10:
            sr = (self.runs / self.balls_faced) * 100
            if sr > 170: pts += 6
            elif sr > 150: pts += 4
            elif sr > 130: pts += 2
        # Bowling
        pts += self.wickets * 25
        pts += self.maidens * 4
        if self.wickets >= 5: pts += 16
        elif self.wickets >= 4: pts += 8
        elif self.wickets >= 3: pts += 4
        # Fielding
        pts += self.catches * 8
        pts += self.stumpings * 12
        pts += self.run_outs * 6
        self.fantasy_points = pts
        return pts

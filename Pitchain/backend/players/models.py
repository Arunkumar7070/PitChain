from django.db import models


class IPLTeam(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)
    logo_url = models.URLField(blank=True)

    class Meta:
        db_table = 'ipl_teams'

    def __str__(self):
        return self.short_name


class Player(models.Model):
    ROLE_CHOICES = [
        ('BAT', 'Batsman'),
        ('BWL', 'Bowler'),
        ('AR', 'All-Rounder'),
        ('WK', 'Wicket-Keeper'),
    ]

    name = models.CharField(max_length=100)
    team = models.ForeignKey(IPLTeam, on_delete=models.CASCADE, related_name='players')
    role = models.CharField(max_length=3, choices=ROLE_CHOICES)
    credit_value = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    is_playing = models.BooleanField(default=True)  # Playing XI flag
    image_url = models.URLField(blank=True)
    ipl_id = models.CharField(max_length=50, unique=True, blank=True)  # External API id

    class Meta:
        db_table = 'players'

    def __str__(self):
        return f"{self.name} ({self.team.short_name})"

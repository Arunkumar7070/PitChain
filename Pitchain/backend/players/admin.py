"""players/admin.py — Admin registration for IPLTeam, Player, PlayerMatchStats."""
from django.contrib import admin
from .models import IPLTeam, Player, PlayerMatchStats

print("[admin] Registering players models...")

@admin.register(IPLTeam)
class IPLTeamAdmin(admin.ModelAdmin):
    list_display  = ('short_name', 'name', 'home_city', 'created_at')
    search_fields = ('name', 'short_name')
    ordering      = ('short_name',)


class PlayerInline(admin.TabularInline):
    model  = Player
    extra  = 0
    fields = ('name', 'role', 'credit_value', 'is_playing')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display  = ('name', 'team', 'role', 'credit_value', 'is_playing', 'ipl_id')
    list_filter   = ('team', 'role', 'is_playing')
    search_fields = ('name', 'ipl_id')
    ordering      = ('team', 'name')
    list_editable = ('is_playing', 'credit_value')


@admin.register(PlayerMatchStats)
class PlayerMatchStatsAdmin(admin.ModelAdmin):
    list_display  = ('player', 'match', 'runs', 'wickets', 'catches', 'fantasy_points', 'updated_at')
    list_filter   = ('match',)
    search_fields = ('player__name',)
    ordering      = ('-fantasy_points',)
    readonly_fields = ('fantasy_points', 'updated_at')

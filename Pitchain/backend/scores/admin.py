"""scores/admin.py — Admin registration for UserTeam, UserTeamPlayer."""
from django.contrib import admin
from .models import UserTeam, UserTeamPlayer

print("[admin] Registering scores models...")

class UserTeamPlayerInline(admin.TabularInline):
    model   = UserTeamPlayer
    extra   = 0
    fields  = ('player', 'is_captain', 'is_vice_captain', 'points_earned')
    readonly_fields = ('points_earned',)


@admin.register(UserTeam)
class UserTeamAdmin(admin.ModelAdmin):
    list_display  = ('user', 'contest', 'total_points', 'rank', 'tx_hash', 'prize_claimed', 'created_at')
    list_filter   = ('contest', 'prize_claimed')
    search_fields = ('user__wallet_address', 'tx_hash')
    ordering      = ('-total_points',)
    readonly_fields = ('total_points', 'rank', 'created_at', 'updated_at')
    inlines       = [UserTeamPlayerInline]


@admin.register(UserTeamPlayer)
class UserTeamPlayerAdmin(admin.ModelAdmin):
    list_display  = ('user_team', 'player', 'is_captain', 'is_vice_captain', 'points_earned')
    list_filter   = ('is_captain', 'is_vice_captain')
    search_fields = ('player__name', 'user_team__user__wallet_address')
    ordering      = ('-points_earned',)

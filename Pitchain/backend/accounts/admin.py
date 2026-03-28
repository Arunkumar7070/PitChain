"""accounts/admin.py — Admin registration for User model."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

print("[admin] Registering accounts models...")

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('wallet_address', 'username', 'is_admin', 'contests_played', 'contests_won', 'total_winnings', 'created_at')
    list_filter   = ('is_admin', 'is_staff', 'is_active')
    search_fields = ('wallet_address', 'username', 'email')
    ordering      = ('-created_at',)
    readonly_fields = ('wallet_address', 'created_at', 'updated_at', 'total_winnings', 'contests_played', 'contests_won')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('🏏 Pitchain', {
            'fields': ('wallet_address', 'is_admin', 'total_winnings', 'contests_played', 'contests_won'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

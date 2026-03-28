"""contests/admin.py — Admin registration for Match, Contest, PrizeDistribution, AdminEarnings."""
from django.contrib import admin
from .models import Match, Contest, PrizeDistribution, AdminEarnings

print("[admin] Registering contests models...")

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display  = ('match_name', 'venue', 'match_date', 'status', 'external_id')
    list_filter   = ('status',)
    search_fields = ('team_a', 'team_b', 'venue', 'external_id')
    ordering      = ('-match_date',)
    list_editable = ('status',)

    @admin.display(description='Match')
    def match_name(self, obj):
        return obj.match_name


class PrizeDistributionInline(admin.TabularInline):
    model   = PrizeDistribution
    extra   = 0
    fields  = ('rank', 'user', 'prize_eth', 'tx_hash', 'distributed_at')
    readonly_fields = ('created_at',)


class AdminEarningsInline(admin.StackedInline):
    model     = AdminEarnings
    extra     = 0
    fields    = ('amount_eth', 'percentage', 'tx_hash', 'recipient_wallet')
    max_num   = 1


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display  = ('name', 'match', 'status', 'entry_fee_eth', 'prize_pool_eth',
                     'participant_count', 'network', 'chain_id', 'contract_contest_id')
    list_filter   = ('status', 'network')
    search_fields = ('name', 'match__team_a', 'match__team_b', 'tx_hash_created')
    ordering      = ('-created_at',)
    readonly_fields = ('prize_pool_eth', 'participant_count', 'created_at', 'updated_at',
                       'network', 'chain_id')
    inlines       = [PrizeDistributionInline, AdminEarningsInline]

    @admin.display(description='Entries')
    def participant_count(self, obj):
        return obj.participant_count


@admin.register(PrizeDistribution)
class PrizeDistributionAdmin(admin.ModelAdmin):
    list_display  = ('contest', 'rank', 'user', 'prize_eth', 'tx_hash', 'distributed_at')
    list_filter   = ('contest',)
    search_fields = ('user__wallet_address', 'tx_hash')
    ordering      = ('rank',)


@admin.register(AdminEarnings)
class AdminEarningsAdmin(admin.ModelAdmin):
    list_display  = ('contest', 'amount_eth', 'percentage', 'recipient_wallet', 'created_at')
    ordering      = ('-created_at',)

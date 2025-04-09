from django.contrib import admin
from .models import FioCurr, Coin, Price_history, Portfolio, Transaction

@admin.register(FioCurr)
class FioCurrAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'price', 'timestamp')
    list_filter = ('symbol', 'timestamp')
    search_fields = ('symbol',)
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('id', 'symbol', 'name', 'marketpriceUSD', 'last_updated')
    list_filter = ('symbol',)
    search_fields = ('name', 'symbol', 'id')
    ordering = ('name',)
    date_hierarchy = 'last_updated'

@admin.register(Price_history)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('asset', 'priceUSD', 'timestamp')
    list_filter = ('asset__symbol', 'timestamp')
    search_fields = ('asset__name', 'asset__symbol')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    raw_id_fields = ('asset',)

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ()

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'asset', 'amount', 'price', 'marketprice', 'time')
    list_filter = ('asset__symbol', 'time')
    search_fields = ('asset__name', 'portfolio__user__username')
    ordering = ('-time',)
    date_hierarchy = 'time'
    raw_id_fields = ('portfolio', 'asset')
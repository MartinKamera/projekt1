from django.contrib import admin
from .models import Portfolio, Coin, Transaction, PriceHistory

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'currency')

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol', 'last_updated')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'coin', 'amount', 'price', 'transaction_type', 'time')
    list_filter = ('transaction_type', 'time')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('coin', 'priceUSD', 'timestamp')
    list_filter = ('timestamp',)
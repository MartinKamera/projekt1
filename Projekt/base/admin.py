from django.contrib import admin
from .models import Portfolio, Coin, Transaction, PriceHistory

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'currency', 'created', 'updated')
    search_fields = ('name', 'user__username')
    list_filter = ('currency',)

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol', 'created', 'updated')
    search_fields = ('id', 'name', 'symbol')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'coin', 'initial_amount', 'price', 'transaction_type', 'created')
    list_filter = ('transaction_type',)
    search_fields = ('portfolio__name', 'coin__name')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('coin', 'priceUSD', 'priceEUR', 'priceCZK', 'priceGBP', 'pricePLN', 'created')
    search_fields = ('coin__name',)

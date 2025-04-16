from django.db import models
from django.contrib.auth.models import User
from enum import Enum

class FiatCurr(models.Model):
    symbol = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=20, decimal_places=3) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol}"

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CZK = "CZK"
    PLN = "PLN"
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]

class Portfolio(models.Model):
    user = models.ForeignKey(User, related_name='portfolios', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices(),
        default=Currency.USD.value
    )
    
    def __str__(self):
        return f"{self.user.username}'s {self.name or 'Default'} portfolio ({self.currency})"

class Coin(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    symbol = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} at {self.marketpriceUSD} USD"

class Transaction(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='transactions', on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=3)
    marketprice = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])

    def __str__(self):
        return f'{self.portfolio} - {self.coin}: {self.amount} at {self.price}'

class Price_history(models.Model):
    coin = models.ForeignKey(Coin, related_name='price_history', on_delete=models.CASCADE)
    priceUSD = models.DecimalField(max_digits=20, decimal_places=3)
    priceEUR = models.DecimalField(max_digits=20, decimal_places=3)
    priceCZK = models.DecimalField(max_digits=20, decimal_places=3)
    priceGBP = models.DecimalField(max_digits=20, decimal_places=3)
    pricePLN = models.DecimalField(max_digits=20, decimal_places=3)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.asset} was {self.priceUSD} USD at {self.timestamp}'
from django.db import models
from django.contrib.auth.models import User

class FioCurr(models.Model):
    symbol = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=20, decimal_places=3) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol}"

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Transaction(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=3)
    marketprice = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.portfolio},{self.marketprice},{self.price}'

class Coin(models.Model):
    id = models.CharField(max_length= 30, primary_key = True)
    symbol = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    marketpriceUSD = models.DecimalField(max_digits=20, decimal_places=3, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.name} at {self.marketpriceUSD} USD"

class Price_history(models.Model):
    asset = models.ForeignKey(Coin, related_name='price_history', on_delete=models.CASCADE)
    priceUSD = models.DecimalField(max_digits=20, decimal_places=3)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.asset} was {self.priceUSD} USD at {self.timestamp}'
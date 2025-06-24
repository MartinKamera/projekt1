from django.db import models
from django.contrib.auth.models import User
from enum import Enum
from collections import defaultdict
import pandas as pd
from decimal import Decimal, ROUND_DOWN
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
import time
import os

class MyabstractModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CZK = "CZK"
    PLN = "PLN"

    @classmethod
    def choices(cls):
        return [(choice.value, choice.name) for choice in cls]

class Portfolio(MyabstractModel):
    user = models.ForeignKey(User, related_name='portfolios', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    free_funds = models.DecimalField(max_digits=20, decimal_places=5, default=Decimal('0.0'))
    total_invested = models.DecimalField(max_digits=20, decimal_places=5, default=Decimal('0.0'))
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices(),
        default=Currency.USD.value
    )
    def get_total_invested(self):
        return self.total_invested.quantize(Decimal("0.00001"), rounding=ROUND_DOWN)

    def get_free_funds(self):
        return self.free_funds.quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
    
    def close_transaction(self, transaction_id):
        try:
            tx = self.transactions.get(id=transaction_id)
            tx.turn_inactive()
            self.free_funds += tx.get_total_value()
            self.save()
            return True
        except Exception as e:
            print(f'nastala chyba:{e}')
            return False
        

    def create_transaction(self, coin, amount, price):
        amount = Decimal(str(amount)) if amount not in (None, "", "None") else Decimal('0')
        price = Decimal(str(price)) if price not in (None, "", "None") else Decimal('0')
        amount = amount.quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        price = price.quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        price_total = (amount * price).quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        free_funds = self.get_free_funds()
        
        try:
            if free_funds == Decimal('0').quantize(Decimal("0.00001")) :
                self.total_invested += price_total
            else:   
                if free_funds > price_total:
                    self.free_funds = free_funds - price_total
                else:
                    price_cut = price_total - free_funds
                    print(price_cut)
                    self.total_invested += price_cut
                    self.free_funds= Decimal('0') 
            self.save() 
            
            transaction = Transaction(
                portfolio=self,
                coin=coin,
                initial_amount=amount,
                price=price,
                transaction_type='Active',
            )
            transaction.full_clean()
            transaction.save()
        
        except:
            print(f'Error creating transaction for {coin} in portfolio {self.name}')
            return None
        return (f'Transaction created: {transaction} at {transaction.created}')

    def getTransactions(self):
        transactions = self.transactions.all()
        
        return transactions

class Coin(MyabstractModel):
    id = models.CharField(max_length=30, primary_key=True)
    symbol = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)

    def get_current_price(self, currency="USD"):
        last_price = cache.get(f'{self.id}_{currency.lower()}_current')
        if last_price is None:
            try:
                latest_entry = self.price_history.order_by('-created').first()
                if latest_entry:
                    last_price = getattr(latest_entry, f'price{currency}', None)
                    if last_price is not None:
                        cache.set(f'{self.id}_{currency.lower()}_current', last_price, timeout=300)
            except PriceHistory.DoesNotExist:
                return None

        return Decimal(last_price).quantize(Decimal("0.00001"), rounding=ROUND_DOWN)

    def update_price_cache(self, price_dict: dict):
        for currency_code, value in price_dict.items():
            cache_key = f'{self.id}_{currency_code.lower()}_current'
            cache.set(cache_key, value)
    
    def get_proc_growth_deltas(self, currency="USD"):
        key = f'{self.id}_{currency.lower()}_growth_stats'
        result = cache.get(key)

        if result is None:
            now = timezone.now()
            periods = {
                "1h": now - timedelta(hours=1),
                "24h": now - timedelta(hours=24),
                "7d": now - timedelta(days=7),
            }

            price_field = f"price{currency.upper()}"
            current_entry = self.price_history.order_by('-created').only(price_field).first()
            current_price = getattr(current_entry, price_field, None) if current_entry else None

            result = {}

            if current_price is None:
                return {key: None for key in periods}

            for label, since in periods.items():
                past_entry = (
                    self.price_history
                    .filter(created__lte=since)
                    .order_by('-created')
                    .only(price_field)
                    .first()
                )
                if past_entry:
                    past_price = getattr(past_entry, price_field, None)
                    if past_price and float(past_price) > 0:
                        try:
                            delta = ((float(current_price) - float(past_price)) / float(past_price)) * 100
                            result[label] = round(delta, 5)
                        except:
                            result[label] = None
                    else:
                        result[label] = None
                else:
                    result[label] = None

            cache.set(key, result, timeout=300)

        return result

class Transaction(MyabstractModel):
    portfolio = models.ForeignKey(Portfolio, related_name='transactions', on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, related_name='transactions', on_delete=models.CASCADE)
    initial_amount = models.DecimalField(max_digits=60, decimal_places=5, default=Decimal('0.0'))
    price = models.DecimalField(max_digits=60, decimal_places=5)
    closed_value = models.DecimalField(max_digits=60, decimal_places=5, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')

    
    def turn_inactive(self):
        self.closed_value = self.get_total_value()
        self.transaction_type = 'Inactive'
        self.save()
    
    def get_closed_value(self):
        return self.closed_value 

    def get_total_value(self):
        price = self.coin.get_current_price(self.portfolio.currency)
        return (Decimal(price) * self.initial_amount).quantize(Decimal("0.00001"), rounding=ROUND_DOWN) if price else Decimal("0")

    def get_profit_loss(self):
        current_value = self.get_total_value()
        initial_value = (self.price * self.initial_amount).quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        profit_loss = (current_value - initial_value).quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        profit_loss_percentage = ((current_value - initial_value) / initial_value * 100).quantize(Decimal("0.00001"), rounding=ROUND_DOWN) if initial_value > 0 else Decimal("0")

        return {
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'current_value': current_value,
            'initial_value': initial_value
        }

    def __str__(self):
        return f'{self.portfolio} - {self.coin}: {self.initial_amount} at {self.price}'

class PriceHistory(MyabstractModel):
    coin = models.ForeignKey(Coin, related_name='price_history', on_delete=models.CASCADE)
    priceUSD = models.DecimalField(max_digits=20, decimal_places=5)
    priceEUR = models.DecimalField(max_digits=20, decimal_places=5)
    priceCZK = models.DecimalField(max_digits=20, decimal_places=5)
    priceGBP = models.DecimalField(max_digits=20, decimal_places=5)
    pricePLN = models.DecimalField(max_digits=20, decimal_places=5)

    class Meta:
        verbose_name = "Price history entry"
        verbose_name_plural = "Price history"
        indexes = [
            models.Index(fields=['created']),  # ⬅⬅⬅ tady
        ]

    def __str__(self):
        return f'{self.coin} was {self.priceUSD} USD at {self.created}'

    
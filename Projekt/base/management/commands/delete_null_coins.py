from django.core.management.base import BaseCommand
from base.models import Coin, PriceHistory

class Command(BaseCommand):
    help = 'Deletes coins without any price history'

    def handle(self, *args, **kwargs):
        cryptos = Coin.objects.all()
        for coin in cryptos:
            
            if not coin.price_history.exists():  
                self.stdout.write(f"Deleting {coin.id} ({coin.symbol}) - no price history")
                coin.delete()
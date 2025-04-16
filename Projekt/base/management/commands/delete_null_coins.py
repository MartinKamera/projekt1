from django.core.management.base import BaseCommand
from base.models import Coin

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        emptyCoins = Coin.objects.filter(marketpriceUSD__isnull = True)


        if emptyCoins.exists:
            for coin in emptyCoins:
                self.stdout.write(f"smazal jsem {coin.id}")
                coin.delete()

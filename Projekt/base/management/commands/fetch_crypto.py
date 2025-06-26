import time
import requests
from django.core.management.base import BaseCommand
from base.models import Coin, PriceHistory, Currency, Coin
from django.utils import timezone
from base.service_classes import CacheService

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        now = timezone.now()

        params = { 
            "ids": ','.join(Coin.objects.values_list('id', flat=True)),
            "vs_currencies": ",".join(["usd", "eur", "czk", "gbp", "pln"]),
            "precision": "5"
        }

        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "CG-zxvhhm4cuPnTntCA9F3y2yTh"
        }

        url = "https://api.coingecko.com/api/v3/simple/price"

        start_fetch = time.perf_counter()
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            CacheService.clear_cache()
                
            json_data = response.json()
            price_history_list = []
            all_coins = {coin.id: coin for coin in Coin.objects.all()}

            for coin_id in json_data:
                try:
                    asset = all_coins.get(coin_id)
                    if not asset:
                        self.stdout.write(self.style.WARNING(f"Coin {coin_id} not found in DB, skipping."))
                        continue

                    for currency in Currency:
                        price = json_data[coin_id].get(currency.name.lower())
                        if price is not None:
                            cache_key = asset.get_cache_key(currency.name)
                            CacheService.set_cache(cache_key, price)

                    price_history_list.append(
                        PriceHistory(
                            coin=asset,
                            priceUSD=json_data[coin_id]['usd'],
                            priceEUR=json_data[coin_id]['eur'],
                            priceCZK=json_data[coin_id]['czk'],
                            priceGBP=json_data[coin_id]['gbp'],
                            pricePLN=json_data[coin_id]['pln']
                        )
                    )

                    self.stdout.write(self.style.SUCCESS(f"Prepared record for {asset.id} at {now}"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error processing {coin_id}: {e}"))

            if price_history_list:
                PriceHistory.objects.bulk_create(price_history_list)
                try:
                    CacheService.set_cache('last_price_update', timezone.now(), timeout=305)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error setting cache: {e}"))
            else:
                self.stdout.write(self.style.WARNING("No records were created in PriceHistory."))

        else:
            self.stdout.write(self.style.WARNING("Connection to coingecko api could not be established"))


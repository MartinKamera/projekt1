import time
import requests
from django.core.management.base import BaseCommand
from base.models import Coin, PriceHistory
from django.utils import timezone
from django.core.cache import cache
from base.service_classes import CoinListService

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        start_total = time.perf_counter()
        now = timezone.now()

        params = { 
            "ids": ",".join(Coin.objects.values_list('id', flat=True)),
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
        self.stdout.write(f"API fetch took {time.perf_counter() - start_fetch:.2f}s")

        if response.status_code == 200:
            try:
                start_clear = time.perf_counter()
                cache.clear()
                self.stdout.write(self.style.SUCCESS(f"Cache cleared successfully in {time.perf_counter() - start_clear:.2f}s"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error clearing cache: {e}"))

            json_data = response.json()
            price_history_list = []
            all_coins = {coin.id: coin for coin in Coin.objects.all()}

            start_processing = time.perf_counter()
            for coin_id in json_data:
                try:
                    asset = all_coins.get(coin_id)
                    if not asset:
                        self.stdout.write(self.style.WARNING(f"Coin {coin_id} not found in DB, skipping."))
                        continue

                    asset.update_price_cache(json_data[coin_id])
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
            self.stdout.write(f"Processing response took {time.perf_counter() - start_processing:.2f}s")

            if price_history_list:
                start_insert = time.perf_counter()
                PriceHistory.objects.bulk_create(price_history_list)
                self.stdout.write(f"DB insert took {time.perf_counter() - start_insert:.2f}s")

                cache.set('last_price_update', timezone.now(), timeout=305)
            else:
                self.stdout.write(self.style.WARNING("No records were created in PriceHistory."))

        else:
            self.stdout.write(self.style.WARNING("Connection to coingecko api could not be established"))

        self.stdout.write(self.style.SUCCESS(f"Total duration: {time.perf_counter() - start_total:.2f}s"))
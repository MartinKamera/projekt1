import requests
from django.core.management.base import BaseCommand
from base.models import Coin, Price_history
class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        params = { 
            "ids": ",".join(Coin.objects.values_list('id', flat = True)),
            "vs_currencies": ",".join(["usd", "eur", "czk", "gbp", "pln"]),
            "precision": "3"
            }

        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "CG-zxvhhm4cuPnTntCA9F3y2yTh"
        }
        
        url = "https://api.coingecko.com/api/v3/simple/price"
        response = requests.get(url, params=params , headers=headers)

        if response.status_code == 200:
            json = response.json()
            
            for coin_id in json:
                asset = Coin.objects.get(id=coin_id)
                
                Price_history.objects.create(
                    coin = asset,
                    priceUSD = json[coin_id]['usd'],
                    priceEUR = json[coin_id]['eur'],
                    priceCZK = json[coin_id]['czk'],
                    priceGBP = json[coin_id]['gbp'],
                    pricePLN = json[coin_id]['pln']
                )

                self.stdout.write(self.style.SUCCESS(f"New record in {asset.id} has been created"))
        
        else:
            self.stdout.write(self.style.WARNING("Connection to geckocoin api could not be established"))
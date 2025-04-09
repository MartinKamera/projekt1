import requests
from django.core.management.base import BaseCommand
from fetchingdata.models import Coin, Price_history
class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        params = { 
            "ids": ",".join(Coin.objects.values_list('id', flat = True)),
            "vs_currencies": "usd",
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
                priceUSD = json[coin_id]['usd']
                asset.marketpriceUSD = priceUSD
                asset.save()

                Price_history.objects.create(
                    asset = asset,
                    priceUSD = priceUSD
                )

        else:
            print("Chyba:", response.status_code)
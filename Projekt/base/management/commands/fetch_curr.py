import requests
from django.core.management.base import BaseCommand
from base.models import FiatCurr

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        req = requests.get("https://v6.exchangerate-api.com/v6/632aedeb5c98ddab4d16de9e/latest/USD")
        
        if req.status_code == 200:
            data = req.json()
            for rate in ["EUR", "GBP", "CZK", "PLN"]:
                curr, created = FiatCurr.objects.get_or_create(
                symbol=rate,
                defaults={'price': data["conversion_rates"][rate]}
                )
                if not created:
                    curr.price = data["conversion_rates"][rate]
                    curr.save()
        
        
         
        

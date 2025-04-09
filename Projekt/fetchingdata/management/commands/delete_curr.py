from django.core.management.base import BaseCommand
from fetchingdata.models import FioCurr  

class Command(BaseCommand):

    def handle(self, *args, **options):
            
        count = FioCurr.objects.all().delete()[0]
      
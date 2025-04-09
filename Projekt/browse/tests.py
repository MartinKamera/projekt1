from django.test import TestCase, Client
from base.models import Coin
from django.urls import reverse

# Create your tests here.
class CoinDetailViewTest(TestCase):
    def setUp(self):
    
        self.coin = Coin.objects.create(
            id='btc',
            name='Bitcoin',
            marketpriceUSD=50000.0
        )
        self.client = Client()

    def test_coin_detail_view(self):
        
        url = reverse('coin_detail', args=[self.coin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['coin'], self.coin)
        self.assertContains(response, self.coin.name)
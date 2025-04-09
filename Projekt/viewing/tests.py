from django.test import TestCase, Client
from fetchingdata.models import Coin
from django.urls import reverse

# Create your tests here.
class CoinDetailViewTest(TestCase):
    def setUp(self):
        # Vytvoření testovacího objektu Coin
        self.coin = Coin.objects.create(
            id='btc',
            name='Bitcoin',
            marketpriceUSD=50000.0
        )
        self.client = Client()

    def test_coin_detail_view(self):
        # Získání URL pro view
        url = reverse('coin_detail', args=[self.coin.id])
        
        # Simulace HTTP požadavku
        response = self.client.get(url)
        
        # Kontrola, že odpověď má status code 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Kontrola, že správný objekt byl předán do šablony
        self.assertEqual(response.context['coin'], self.coin)
        
        # Kontrola, že obsah odpovědi obsahuje název kryptoměny
        self.assertContains(response, self.coin.name)
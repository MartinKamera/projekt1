from django.test import TestCase
from django.test import TestCase, Client
from base import models as m
from django.urls import reverse
from django.contrib.auth.models import User

class CoinDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
       
        self.coin_btc = m.Coin.objects.create(id='btc', symbol='BTC', name='Bitcoin')
        self.coin_eth = m.Coin.objects.create(id='eth', symbol='ETH', name='Ethereum')
        self.coin_xrp = m.Coin.objects.create(id='xrp', symbol='XRP', name='Ripple')

    
        self.user = User.objects.create_user(
            username="TestUser",
            email="testovaciemal@seznam.cz",
            password="testpassword"
        )
        self.portfolio = m.Portfolio.objects.create(
            user=self.user,
            name='Main Portfolio',
            currency='USD'
        )

       
        m.Transaction.objects.create(
            portfolio=self.portfolio,
            coin=self.coin_btc,
            amount=1.5,
            marketprice=30000,
            price=29000,
            transaction_type='BUY'
        )
        m.Transaction.objects.create(
            portfolio=self.portfolio,
            coin=self.coin_btc,
            amount=0.5,
            marketprice=32000,
            price=31000,
            transaction_type='SELL'  
        )
        m.Transaction.objects.create(
            portfolio=self.portfolio,
            coin=self.coin_eth,
            amount=2.0,
            marketprice=2000,
            price=1900,
            transaction_type='BUY'
        )
        m.Transaction.objects.create(
            portfolio=self.portfolio,
            coin=self.coin_xrp,
            amount=500,
            marketprice=1,
            price=0.9,
            transaction_type='BUY'
        )

        m.Transaction.objects.create(
            portfolio=self.portfolio,
            coin=self.coin_eth,
            amount=1.0,
            marketprice=2100,
            price=2050,
            transaction_type='SELL'
        )

    def test_get_transactions_groups_by_coin_and_ignores_sell(self):
        transactions_by_coin = self.portfolio.getTransactions()

        self.assertIn('btc', transactions_by_coin)
        self.assertIn('eth', transactions_by_coin)
        self.assertIn('xrp', transactions_by_coin)
        self.assertNotIn('doge', transactions_by_coin)
        self.assertEqual(len(transactions_by_coin['btc']), 1)  
        self.assertEqual(len(transactions_by_coin['eth']), 1)
        self.assertEqual(len(transactions_by_coin['xrp']), 1)
        btc_transaction = transactions_by_coin['btc'][0]
        self.assertEqual(btc_transaction.amount, 1.5)
        self.assertEqual(btc_transaction.transaction_type, 'BUY')
        self.assertCountEqual(transactions_by_coin.keys(), ['btc', 'eth', 'xrp'])


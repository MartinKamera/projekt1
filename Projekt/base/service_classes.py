from base.models import Coin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import pandas as pd
import time
from collections import defaultdict
from functools import wraps


class CoinListService:

    
    def __init__(self, currency="USD", preloaded_coins=None):
        self.currency = currency.upper()
        self.cache_key = f"coinlist_with_prices_{self.currency.lower()}"
        self.coinlist = None
        self.preloaded_coins = preloaded_coins

    def get_coinlist(self, query=None, sort_by_growth=None, ascending=False, cache_set_only = False):
        if self.coinlist is None:
            self.coinlist = cache.get(self.cache_key)
        if self.coinlist is None:
            self.coinlist = self.build_coinlist()
            cache.set(self.cache_key, self.coinlist, timeout=300)
        if cache_set_only:
            return None

        filtered = self.filter_by_query(query) if query else self.coinlist

        if sort_by_growth in {"1h", "24h", "7d"}:
            return sorted(
                filtered,
                key=lambda c: c.get("growth", {}).get(sort_by_growth) if c.get("growth", {}).get(sort_by_growth) is not None else float("-inf"),
                reverse=not ascending 
            )
            
        return filtered

    def build_coinlist(self):
        coins = self.preloaded_coins or Coin.objects.all()
        coins_dict = {coin.id: coin for coin in coins}
        coinlist = []
        total_growth_time = 0.0

        for coin_id, coin in coins_dict.items():
            current_price = float(coin.get_current_price(self.currency) or 0)

            start_growth = time.perf_counter()
            growths = coin.get_proc_growth_deltas(self.currency)
            duration = time.perf_counter() - start_growth
            total_growth_time += duration

            coinlist.append({
                "id": coin.id,
                "name": coin.name,
                "symbol": coin.symbol,
                "current_price": current_price,
                "growth": growths,
            })
        return coinlist

    def filter_by_query(self, query):
        q = query.lower()
        return [coin for coin in self.coinlist
                if (coin["name"] and q in coin["name"].lower()) or
               (coin["symbol"] and q in coin["symbol"].lower())]
        
class CoindDetailsService:
    
    def __init__(self, coin_id, currency, period):
        self.coin_id = coin_id
        self.currency = currency.lower()
        self.period = period
        self.cache_key = f"ohlc_{coin_id}_{self.currency}_{period}"


    def get_ohlc_data(self):
        ohlc_data = cache.get(self.cache_key)
        if ohlc_data is None:
            ohlc_data = self.build_ohlc_data()
            cache.set(self.cache_key, ohlc_data, timeout=300)
        return ohlc_data

    def build_ohlc_data(self):
        now = timezone.now()
        coin = Coin.objects.get(id=self.coin_id)
        period_map = {
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
        }
        since = now - period_map.get(self.period, timedelta(days=1))
        queryset = coin.price_history.filter(created__gte=since).order_by('created')
        if not queryset.exists():
            return {"x": [], "open": [], "high": [], "low": [], "close": []}

        price_field = f"price{self.currency.upper()}"
        
        data = []
        for price in queryset:
            value = getattr(price, price_field, None)
            if value is not None:
                data.append({
                    'timestamp': price.created,
                    'price': float(value),
                })
        if not data or len(data) < 2:
            return {"x": [], "open": [], "high": [], "low": [], "close": []}

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp').sort_index()

        target_candles = 60
        
        total_seconds = (df.index[-1] - df.index[0]).total_seconds()
        if total_seconds <= 0:
            return {"x": [], "open": [], "high": [], "low": [], "close": []}

        interval_seconds = max(1, int(total_seconds / target_candles))
        if interval_seconds < 60:
            freq = f"{interval_seconds}s"
        elif interval_seconds < 3600:
            freq = f"{interval_seconds // 60}min"
        elif interval_seconds < 86400:
            freq = f"{interval_seconds // 3600}h"
        else:
            freq = f"{interval_seconds // 86400}d"

        ohlc = df['price'].resample(freq).ohlc().dropna()
        x = [idx.isoformat() for idx in ohlc.index]
        open_ = [float(x) for x in ohlc['open']]
        high = [float(x) for x in ohlc['high']]
        low = [float(x) for x in ohlc['low']]
        close = [float(x) for x in ohlc['close']]

        return {
            "x": x,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
        }
    
    
    def get_last_price(self):
        last_price = cache.get(f'{self.coin_id}_{self.currency.lower()}_current')
        return last_price if last_price is not None else Coin.objects.get(id=self.coin_id).get_current_price(self.currency)

class PortfolioSummaryService:
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.cache_key = f"portfolio_summary_{portfolio.id}"

    def get_summary(self):
        summary = cache.get(self.cache_key)
        if summary is None:
            summary = self.build_summary()
            cache.set(self.cache_key, summary, timeout=300)
        return summary

    def build_summary(self):
        self.portfolio.refresh_from_db()
        tx_by_coin = self.get_transactions_grouped_by_coin("Active")

        coin_tabs, active_value = self.build_coin_tabs(tx_by_coin)

        free_funds = float(self.portfolio.get_free_funds())
        total_invested = float(self.portfolio.get_total_invested())
        total_value = active_value + free_funds
        profit_abs = total_value - total_invested
        profit_pct = (profit_abs / total_invested * 100) if total_invested > 0 else 0.0

        return {
            "coin_tabs": coin_tabs,
            "portfolio_currency": self.portfolio.currency,
            "total_invested": total_invested,
            "free_funds": free_funds,
            "active_total_value": active_value,
            "total_value": total_value,
            "total_profit_abs": profit_abs,
            "total_profit_pct": profit_pct,
        }

    def get_transactions_grouped_by_coin(self, transaction_type="Active"):
        transactions = self.portfolio.transactions.filter(transaction_type=transaction_type).select_related('coin').order_by('-created')
        coin_dict = defaultdict(list)
        for tx in transactions:
            coin_dict[tx.coin].append(tx)
        return coin_dict

    def build_coin_tabs(self, tx_by_coin):
        coin_tabs = []
        active_value = 0.0

        for coin, txs in sorted(tx_by_coin.items(), key=lambda item: item[0].name.lower()):
            total_buy = sum(tx.price * tx.initial_amount for tx in txs)
            total_now = sum(tx.get_total_value() for tx in txs)
            total_amount = sum(tx.initial_amount for tx in txs)
            profit_abs = total_now - total_buy if total_buy else 0.0
            profit_pct = (profit_abs / total_buy * 100) if total_buy else 0.0

            active_value += float(total_now)

            coin_tabs.append({
                "coin": {
                    "id": coin.id,
                    "name": coin.name,
                    "symbol": coin.symbol,
                },
                "total_amount": total_amount,
                "transactions": [self.serialize_transaction(tx) for tx in txs],
                "profit_pct": profit_pct,
                "profit_abs": profit_abs,
                "total_buy": total_buy,
                "total_now": total_now,
            })

        return coin_tabs, active_value

    def serialize_transaction(self, tx):
        profit = tx.get_profit_loss() or {}
        return {
            "id": tx.id,
            "amount": float(tx.initial_amount),
            "price": float(tx.price * tx.initial_amount),
            "created": tx.created.strftime("%Y-%m-%d %H:%M"),
            "total_buy_value": float(tx.initial_amount * tx.price),
            "profit_loss": float(profit.get("profit_loss")) if profit.get("profit_loss") is not None else None,
            "profit_loss_percentage": float(profit.get("profit_loss_percentage")) if profit.get("profit_loss_percentage") is not None else None,
            "current_price": float(tx.get_total_value()) if tx.get_total_value() is not None else None,
        }
    
def require_cache_online(default_return=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CacheService.checked:
                CacheService._check_connection()
            if not CacheService.online:
                return default_return
            return func(*args, **kwargs)
        return wrapper
    return decorator


class CacheService:
    online = None      
    checked = False    

    @staticmethod
    def _check_connection():
        try:
            cache.get('test_cache_connection')
            CacheService.online = True
        except Exception:
            CacheService.online = False
            print("Cache is not available. Some features may not work correctly.")
        CacheService.checked = True

    @staticmethod
    @require_cache_online()
    def clear_cache(key=None):
        if key:
            try:
                cache.delete(key)
            except Exception as e:
                raise RuntimeError(f"Error clearing cache for {key}: {e}")
            return
        else:
            try:
                cache.clear()
            except Exception as e:
                raise RuntimeError(f"Error clearing cache: {e}")

    @staticmethod
    @require_cache_online()
    def set_cache(key, value, timeout=300):
        try:
            cache.set(key, value, timeout=timeout)
        except Exception as e:
            raise RuntimeError(f"Error setting cache for {key}: {e}")

    @staticmethod
    @require_cache_online(default_return=None)
    def get_cache(key):
        try:
            return cache.get(key)
        except Exception as e:
            raise RuntimeError(f"Error getting cache for {key}: {e}")
        

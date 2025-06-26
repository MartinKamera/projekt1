from base.models import Portfolio, PriceHistory
from django.contrib.auth.models import User
from django.core.cache import cache
from base.service_classes import CacheService


def get_active_portfolio(request):
    if not request.user.is_authenticated:
        return None
    portfolio = None
    active_portfolio_id = request.session.get('active_portfolio_id')
    cache_key = f'active_portfolio_{request.user.id}'
    if active_portfolio_id:
        portfolio = cache.get(cache_key)
        if not portfolio:
            try:
                portfolio = Portfolio.objects.get(id=active_portfolio_id)
                cache.set(cache_key, portfolio, timeout=3600)
            except Portfolio.DoesNotExist:
                portfolio = None
    return portfolio

def get_user_portfolios(request, portfolio_id=None):
    if not request.user.is_authenticated:
        return []
    cache_key = f'user_portfolios_{request.user.id}'
    portfolios = CacheService.get_cache(cache_key)
    if portfolios is None:
        portfolios = list(Portfolio.objects.filter(user=request.user))
        CacheService.set_cache(cache_key, portfolios, timeout=3600)
    if portfolio_id:
        try:
            portfolio = next(p for p in portfolios if p.id == portfolio_id)
            return portfolio
        except StopIteration:
            return None
    return portfolios

def last_updated():
    last_update = CacheService.get_cache('last_price_update')
    if last_update is None:
        last_update = PriceHistory.objects.order_by('-created').first()
        CacheService.set_cache('last_price_update', last_update.created, timeout=305) if last_update else None

    return last_update.strftime('%Y-%m-%d %H:%M:%S')

def invalidate_active_portfolio_cache(request):
    if request.user.is_authenticated:
        cache_key = f'active_portfolio_{request.user.id}'
        CacheService.clear_cache(cache_key)




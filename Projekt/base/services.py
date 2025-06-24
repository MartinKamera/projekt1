from base.models import Portfolio
from django.contrib.auth.models import User
from django.core.cache import cache


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
    portfolios = cache.get(cache_key)
    if portfolios is None:
        portfolios = list(Portfolio.objects.filter(user=request.user))
        cache.set(cache_key, portfolios, timeout=300)
    if portfolio_id:
        try:
            portfolio = next(p for p in portfolios if p.id == portfolio_id)
            return portfolio
        except StopIteration:
            return None
    return portfolios

def invalidate_active_portfolio_cache(request):
    if request.user.is_authenticated:
        cache_key = f'active_portfolio_{request.user.id}'
        cache.delete(cache_key)




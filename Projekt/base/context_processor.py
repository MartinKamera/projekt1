from base.models import Portfolio 
from django.core.cache import cache
from base.services import get_user_portfolios

def user_portfolios(request):
    if request.user.is_authenticated:
        portfolios = get_user_portfolios(request)
        return {'user_portfolios': portfolios}
    return {'user_portfolios': []}

def last_updated(request):
    last_updated = cache.get('last_price_update')
    return {'last_updated': last_updated}
from base.models import Coin, Portfolio
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
import json

def coin_detail(request, coin_id):
    crypto = get_object_or_404(Coin, id=coin_id)
    currency = 'USD'
    
    if request.user.is_authenticated:
        active_portfolio_id = request.session.get('active_portfolio_id') 
        if active_portfolio_id:
            try:
                active_portfolio = Portfolio.objects.get(id=active_portfolio_id)
                currency = active_portfolio.currency
            except Portfolio.DoesNotExist:
                pass
    raw_data = crypto.get_price_data(currency=currency)  
    context = {
        'coin': crypto,
        'chart_data': raw_data,
        'currency': currency,
    }
    print("Tohle je context")
    print(context)
    return render(request, 'coin_view.html', context)

def home(request):
    return render(request, 'home.html')

def coin_list(request):
    query = request.GET.get('query')
    currency = 'USD'

    
    if query:
        coins = Coin.objects.filter(name__icontains=query)
    else:
        coins = Coin.objects.all()
    
    if request.user.is_authenticated:
        active_portfolio_id = request.session.get('active_portfolio_id') 
        if active_portfolio_id:
            try:
                active_portfolio = Portfolio.objects.get(id=active_portfolio_id)
                currency = active_portfolio.currency
            except Portfolio.DoesNotExist:
               pass
        else:
            currency = 'USD'
        
    coin_data = []
    for coin in coins:
        market_price = coin.get_current_price(currency=currency)
        coin_data.append({
            'id': coin.id,
            'name': coin.name,
            'symbol': coin.symbol,
            'price': market_price['price'],
            'last_updated': market_price['last_updated'],
            
        })
    
    context = {
        'coin_list': coin_data,
        'currency': currency,
        'query': query,
    }

    return render(request, 'coin_list.html', context)

@login_required
def portfolioSelection(request):
    if request.method == 'POST':
        try:
            query = request.POST.get('switch')
            portfolio = Portfolio.objects.get(id=query)
            request.session['active_portfolio_id'] = portfolio.id
        
        except Portfolio.DoesNotExist:
            portfolio = None
            request.session['active_portfolio_id'] = None
        finally:
            referer = request.META.get('HTTP_REFERER')

    return redirect(referer)


    


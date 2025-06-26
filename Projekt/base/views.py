from django.shortcuts import render, redirect
from base.form_class_extention import PortfolioCreationForm
from base.models import Portfolio, Coin, Portfolio 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from base.form_class_extention import LoginForm
from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST, require_GET
from base.services import get_active_portfolio, get_user_portfolios, invalidate_active_portfolio_cache
from base.service_classes import CoinListService, CoindDetailsService, PortfolioSummaryService, CacheService
from django.utils import timezone
from decimal import Decimal, ROUND_DOWN
import time
 

@never_cache
@login_required
def portfolio_creation(request):
    if request.method == 'POST':
        form = PortfolioCreationForm(request.POST)
        if form.is_valid():
            currency = form.cleaned_data["portfolio_currency"]
            name = form.cleaned_data["portfolio_name"]
            user = request.user
            portfolio = Portfolio.objects.create(
                name=name,
                currency=currency,
                user=user
            )
            CacheService.clear_cache(f'user_portfolios_{user.id}')
            CacheService.clear_cache(f'active_portfolio_{user.id}')
            
            request.session['active_portfolio_id'] = portfolio.id
            
            return render(request, 'redirect_replace.html', {'target_url': reverse('coin_list')})
    else: 
        form = PortfolioCreationForm()
    
    return render(request, 'portfolio_creation.html', {'form': form})    

@never_cache
def register(request):
    if request.user.is_authenticated:  
        return redirect('coin_list')
    
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            return redirect('login')
    
    else:
        form = UserCreationForm()

    return render(request, 'registration.html', {'form': form})

@never_cache
def login(request):
    if request.user.is_authenticated:
        return render(request, 'redirect_replace.html', {'target_url': reverse('coin_list')})

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )

        if user is not None:
            auth_login(request, user)
            portfolios = Portfolio.objects.filter(user=user)
            if portfolios.exists():
                active_portfolio = portfolios.first()
                request.session['active_portfolio_id'] = active_portfolio.id
                CacheService.set_cache(f'active_portfolio_{user.id}', active_portfolio, timeout=3600)
                return render(request, 'redirect_replace.html', {'target_url': reverse('coin_list')})
            else:
                return render(request, 'redirect_replace.html', {'target_url': reverse('portfolio_creation')})

        messages.error(request, "Invalid username or password.")

    return render(request, 'login.html', {'form': form})

@never_cache
@login_required
def logout(request):
    if request.user.is_authenticated:
        CacheService.clear_cache(f'active_portfolio_{request.user.id}')
        CacheService.clear_cache(f'user_portfolios_{request.user.id}')
        auth_logout(request)
    return render(request, 'redirect_replace.html', {'target_url': reverse('coin_list')})

 
@never_cache
def coin_detail(request, coin_id):
    currency = 'USD'
    period = request.GET.get("period", "24h")
    portfolio = get_active_portfolio(request)

    if portfolio:
        currency = portfolio.currency

    service = CoindDetailsService(coin_id, currency, period)
    ohlc_data = service.get_ohlc_data()
    last_price = service.get_last_price()

    context = {
        "coin": Coin.objects.get(id=coin_id),
        "currency": currency,
        "plotly_data": ohlc_data,
        "interval": period,
        "selected_period": period,
        "last_price": last_price,
        
    }
    return render(request, "coin_view.html", context)

@never_cache
def ajax_coin_detail(request, coin_id):
    currency = 'USD'
    period = request.GET.get("period", "24h")
    portfolio = get_active_portfolio(request)
    if portfolio:
        currency = portfolio.currency
    
    service = CoindDetailsService(coin_id, currency, period)
    ohlc_data = service.get_ohlc_data()
    last_price = service.get_last_price()

    last_updated = CacheService.get_cache('last_price_update')
    last_updated_str = last_updated.isoformat() if last_updated else None

    coin = Coin.objects.get(id=coin_id)
    response = {
        "coin": {
            "id": coin.id,
            "name": coin.name,
            "symbol": coin.symbol,
        },
        "ohlc_data": ohlc_data,
        "last_price": last_price,
        "currency": currency,
        "period": period,
        "last_updated": last_updated_str,
    }
    return JsonResponse(response)

@never_cache
def home(request):
    if request.user.is_authenticated:
        portfolios = get_user_portfolios(request)
        if portfolios:
            request.session['active_portfolio_id'] = portfolios[0].id
            return redirect('coin_list')
        else:
            return redirect('portfolio_creation')
    return render(request, 'home.html')

@never_cache
def coin_list(request):
    return render(request, 'coin_list.html')

@never_cache
def ajax_search_coins(request):
    query = request.GET.get('query', '')
    sort_by_growth = request.GET.get('sort')  
    direction = request.GET.get('direction')  
    currency = 'USD'
    portfolio = get_active_portfolio(request)
    if portfolio:
        currency = portfolio.currency

    ascending = direction == "falling"  
    service = CoinListService(currency)
    coins = service.get_coinlist(query=query, sort_by_growth=sort_by_growth, ascending=ascending)
    last_updated = CacheService.get_cache('last_price_update')
    last_updated_str = last_updated.isoformat() if last_updated else None

    data = [
        {
            'id': coin['id'],
            'name': coin['name'],
            'symbol': coin['symbol'],
            'price': coin['current_price'],
            'growth': coin['growth'],
        }
        for coin in coins
    ]
    response = {
        "coins": data,
        "currency": currency,
        "last_updated": last_updated_str,
    }
    return JsonResponse(response)

@never_cache
@login_required
def portfolioSelection(request):
    if request.method == 'POST':
        try:
            portfolio_id = request.POST.get('switch')
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
            request.session['active_portfolio_id'] = portfolio.id
            CacheService.set_cache(f'active_portfolio_{request.user.id}', portfolio, timeout=3600)
        except Portfolio.DoesNotExist:
            request.session['active_portfolio_id'] = None
            CacheService.clear_cache(f'active_portfolio_{request.user.id}')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        
        return render(request, 'redirect_replace.html', {'target_url': reverse('coin_list')})


@login_required
@require_POST
def buy_crypto(request):
    if not get_active_portfolio(request):
        return JsonResponse({"status": "error", "message": "No portfolio found"}, status=400)
    portfolio = get_active_portfolio(request)
    if not portfolio:
        return JsonResponse({"status": "error", "message": "No active portfolio"}, status=400)

    coin_id = request.POST.get('coin_id')
    try:
        coin = Coin.objects.get(id=coin_id)
    except Coin.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Coin not found"}, status=404)

    method = request.POST.get('method')
    if method == "by_amount":
        raw_amount = request.POST.get('value')
        if not raw_amount:
            return JsonResponse({"status": "error", "message": "Enter a valid amount."})
        try:
            amount = Decimal(raw_amount).quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        except:
            return JsonResponse({"status": "error", "message": "Invalid amount"})
        if amount <= Decimal("0"):
            return JsonResponse({"status": "error", "message": "Enter a valid amount."})
        price = Decimal(str(coin.get_current_price(portfolio.currency))).quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        portfolio.create_transaction(coin=coin, amount=amount, price=price)
        CacheService.clear_cache(f'portfolio_summary_{portfolio.id}')
        invalidate_active_portfolio_cache(request)
        
        return JsonResponse({
            "status": "ok",
            "message": f"Bought {amount} {coin.symbol}"
        })

    elif method == "by_value":
        raw_value = request.POST.get('value')
        if not raw_value:
            return JsonResponse({"status": "error", "message": "Enter a valid value."})
        try:
            value = Decimal(raw_value).quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        except:
            return JsonResponse({"status": "error", "message": "Invalid value"})

        price = coin.get_current_price(portfolio.currency)
        if not price:
            return JsonResponse({"status": "error", "message": "No current price."})
        price = Decimal(str(price)).quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        if value <= Decimal("0"):
            return JsonResponse({"status": "error", "message": "Enter a valid value."})

        amount = (value / price).quantize(Decimal("0.00001"), rounding=ROUND_DOWN)
        portfolio.create_transaction(coin=coin, amount=amount, price=price)
        CacheService.clear_cache(f'portfolio_summary_{portfolio.id}')
        invalidate_active_portfolio_cache(request)
        return JsonResponse({
            "status": "ok",
            "message": f"Bought {amount} {coin.symbol}"
        })

    else:
        return JsonResponse({"status": "error", "message": "Invalid method."})

@never_cache
@login_required
def my_transactions(request, portfolio_id=None):
    if portfolio_id is None:
        portfolio = get_active_portfolio(request)
    else:
        portfolio = get_user_portfolios(request, portfolio_id)

    if not portfolio:
        return redirect("portfolio_creation")
    summary_service = PortfolioSummaryService(portfolio)
    context = summary_service.get_summary()
    context['last_price_update'] = cache.get('last_price_update')
    return render(request, "portfolio_summary.html", context)

@require_GET
@login_required
def ajax_my_transactions(request, portfolio_id=None):
    if portfolio_id:
        portfolio = get_user_portfolios(request, portfolio_id)
        if not portfolio:
            return JsonResponse({"error": "Portfolio not found."}, status=404)
    else:
        portfolio = get_active_portfolio(request)
        if not portfolio:
            return JsonResponse({"error": "No active portfolio."}, status=400)
        
    summary_service = PortfolioSummaryService(portfolio)
    summary = summary_service.get_summary()

    coins_data = []
    for tab in summary['coin_tabs']:
        coins_data.append({
            "id": tab["coin"]["id"],
            "name": tab["coin"]["name"],
            "symbol": tab["coin"]["symbol"],
            "transactions": tab["transactions"],
            "total_buy": float(tab["total_buy"]),
            "total_now": float(tab["total_now"]),
            "profit_abs": float(tab["profit_abs"]),
            "profit_pct": float(tab["profit_pct"]),
            "total_amount": float(tab["total_amount"])
        })

    last_updated = CacheService.get_cache('last_price_update')

    return JsonResponse({
        "coins": coins_data,
        "portfolio_name": portfolio.name,
        "portfolio_currency": summary["portfolio_currency"],
        "last_price_update": last_updated.isoformat() if last_updated else None,
        "total_invested": float(summary["total_invested"]),
        "total_value": float(summary["total_value"]),
        "free_funds": float(summary["free_funds"]),
        "total_profit_abs": float(summary["total_profit_abs"]),
        "total_profit_pct": float(summary["total_profit_pct"]),
        "active_total_value": float(summary["active_total_value"])
    })


@require_POST
@login_required
def ajax_sell(request):
    portfolio = get_active_portfolio(request)
    print("TOTAL INVESTED after ajax_sell:", portfolio.total_invested)

    if not portfolio:
        return JsonResponse({"status": "error", "message": "No active portfolio"}, status=400)

    tx_id = request.POST.get('transaction_id')

    try:
        tx = portfolio.transactions.get(id=tx_id, transaction_type='Active')
    except:
        return JsonResponse({"status": "error", "message": "Transaction not found"}, status=404)

    success = portfolio.close_transaction(tx_id)
    print("TOTAL INVESTED after ajax_sell:", portfolio.total_invested)

    if success:
        cache.delete(f'portfolio_summary_{portfolio.id}')
        invalidate_active_portfolio_cache(request)
        return JsonResponse({
            "status": "ok",
            "message": f"Transaction closed. {tx.get_total_value()} {portfolio.currency} added to free funds."
        })

    return JsonResponse({"status": "error", "message": "Could not close the transaction."})

@never_cache
@login_required
def portfolio_list(request):
    portfolios = get_user_portfolios(request)
    portfolio_data = []
    for portfolio in portfolios:
        summary_service = PortfolioSummaryService(portfolio)
        summary = summary_service.get_summary()
        portfolio_data.append({
            "id": portfolio.id,
            "name": portfolio.name,
            "currency": portfolio.currency,
            "is_active": True if portfolio.id == request.session.get('active_portfolio_id') else False, 
            "created": portfolio.created.strftime("%Y-%m-%d %H:%M"),
            "total_invested": summary["total_invested"],
            "total_value": summary["total_value"],
            "profit_abs": float(summary["total_value"]) - float(summary["total_invested"]),
            "profit_pct": (float(summary["total_value"]) - float(summary["total_invested"])) / float(summary["total_invested"]) * 100 if float(summary["total_invested"]) > 0 else 0,


        })
    return render(request, 'portfolio_list.html', {
        'portfolio_data': portfolio_data,
    })

@never_cache
@require_POST
@login_required
def ajax_delete_portfolio(request):
    portfolio_id = request.POST.get("portfolio_id")
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        portfolio.delete()
        CacheService.clear_cache(f'user_portfolios_{request.user.id}')
        if request.session.get('active_portfolio_id') == int(portfolio_id):
            CacheService.clear_cache(f'active_portfolio_{request.user.id}')
            request.session['active_portfolio_id'] = None
        return JsonResponse({"status": "ok", "message": "Portfolio deleted successfully"})
    except Portfolio.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Portfolio not found"}, status=404)
        
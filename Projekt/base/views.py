from django.shortcuts import render, redirect
from base.form_class_extention import PortfolioCreationForm
from base.models import Portfolio, Coin, User, Portfolio
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from base.form_class_extention import LoginForm
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
import json

@login_required
def portfolioCreation(request):
    if request.method == 'POST':
        form = PortfolioCreationForm(request.POST)
        
        if form.is_valid():
            currency = form.cleaned_data["portfolio_currency"]
            name = form.cleaned_data["portfolio_name"]
            user = request.user
            Portfolio.objects.create(
                name = name,
                currency = currency,
                user = user
            )
            messages.success(request, "Portfolio successfully created")
            
            return redirect('coin_list')
    else: 
        form = PortfolioCreationForm()

    return render(request, 'portfolio_creation.html', {'form': form})    

def register(request):
    if request.user.is_authenticated:  
        return redirect('coin_list')
    
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration has been successful, redirecting you to the login page.")
            return redirect('login')
    
    else:
        form = UserCreationForm()

    return render(request, 'registration.html', {'form': form})


def login(request):
    if request.user.is_authenticated:
        return redirect('coin_list')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )

        if user is not None:
            auth_login(request, user)
            portfolios = portfolios = Portfolio.objects.filter(user=user)
            
            if portfolios.exists():
                request.session['active_portfolio_id'] = portfolios.first().id
                return redirect(request.META.get('HTTP_REFERER') or reverse('coin_list'))
            else:
                return redirect('portfolio_creation')
        
        messages.error(request, "Invalid username or password.")

    return render(request, 'login.html', {'form': form})

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
        

        messages.error(request, "You are not logged in.")
    referer = request.META.get('HTTP_REFERER')

    
    return redirect(referer)
 
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


        

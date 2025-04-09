from django.shortcuts import render
from base.models import Coin
from django.shortcuts import render, get_object_or_404

def coin_detail(request, coin_id):
    crypto = get_object_or_404(Coin, id = coin_id)
    context = {
        'coin': crypto
    }
    return render(request, 'coin_view.html', context )

def home(request):
    return render(request, 'home.html')

def coin_list(request):
    query = request.GET.get('query')
    coins = Coin.objects.all()

    if query:
        coins = coins.filter(name__icontains=query) | coins.filter(symbol__icontains=query)

    context = {
        'coin_list': coins
    }

    return render(request, 'coin_list.html', context)



    


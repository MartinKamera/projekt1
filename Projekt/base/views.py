from django.shortcuts import render, redirect
from base.form_class_extention import PortfolioCreationForm
from base.models import Portfolio
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Create your views here.
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


        

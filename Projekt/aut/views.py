from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from base.form_class_extention import LoginForm
from base.models import Portfolio


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

            try:
                portfolios = Portfolio.objects.filter(user=user)
                request.session['active_portfolio_id'] = portfolios[0].id
                return redirect(request.META.get('HTTP_REFERER'))
            
            except Portfolio.DoesNotExist:
                return redirect('portfolio_creation')
        
        messages.error(request, "Invalid username or password.")

    return render(request, 'login.html', {'form': form})

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
        

        messages.error(request, "You are not logged in.")
    referer = request.META.get('HTTP_REFERER')

    
    return redirect(referer)

                                



    

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from base.form_class_extention import LoginForm
from base.models import Portfolio



# Create your views here.
def register(request):
    if request.user.is_authenticated:  
        return redirect('coin_list')
    
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration has been successful, redirecting you to the login page.")
            return redirect('login_html')
    
    else:
        form = UserCreationForm()

    return render(request, 'registration.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('coin_list')
    
    if request.method == 'POST':
        form = LoginForm(request, data = request.POST)
        
        if form.is_valid():
            user = authenticate(request, username = form.cleaned_data('username'), password = form.cleaned_data('password'))
            
            if user is not None:
                login(request, user)
                
                try:
                    portfolio = Portfolio.objects.get(user = user)
                    messages.success(request, f'Welcome back, {user.username}')
                    return redirect('coin_list')

                except Portfolio.DoesNotExist:
                    messages.success(request, f'Welcome to the crypto tracker, {user.username}. In order to fully utilize, please create your first portfolio accordingly to your needs and wishes')
                    return redirect('portfolio_creation')

        else:
            messages.error(request, "Invalid username or password.")
        
    else:
        
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


    


                                



    

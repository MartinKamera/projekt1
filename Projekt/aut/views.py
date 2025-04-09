from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login

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
        

    

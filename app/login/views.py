from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout


# Create your views here.

# LOGIN function
def login(request):
    if request.method == 'POST':
        uname = request.POST['user-name']
        password = request.POST['user-pass']

        user = auth.authenticate(username=uname,password=password)
    
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'USER NOT FOUND')
            return redirect('login')
    else:
        return redirect('login')

# LOGOUT function
def logout(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'home.html', {})

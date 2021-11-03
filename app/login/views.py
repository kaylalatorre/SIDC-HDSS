from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth, User, Group
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
        return render(request, 'login.html', {})

# LOGOUT function
def logout_view(request):
    logout(request)
    # TEST
    print("TEST LOG: User signed out.")
    return redirect('login')

def home(request, *args, **kwargs):

    for g in Group.objects.filter():
        if g.name == request.user.groups.all()[0].name:
            # TEST: for tracking group name of User
            print("TEST LOG: USERTYPE-- " + request.user.groups.all()[0].name)

            print("TEST LOG: in Home view/n")
            print(request.user.groups.all()[0].name)
            # ENDTEST

            # context = {
            #     'user_group': request.user.groups.all()[0].name
            # }

    return render(request, 'home.html', {})

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
            # messages.error(request, 'USER NOT FOUND') # ERROR: 404, "User not found."
            # return redirect('login')

            # TODO: idk if this works.
            error = {'code': 404, 
                'message': 'User not found'
            }
  
            return render(request, 'login.html', error)
    else:
        return render(request, 'login.html', {})

# LOGOUT function
def logout_view(request):
    logout(request)
    
    print("TEST LOG: User signed out.")
    return redirect('login')

def home(request, *args, **kwargs):
    print("TEST LOG: in Home view/n")

    try:
        hasUsertype = True

        for g in Group.objects.filter():
            if g.name == request.user.groups.all()[0].name:
                # TEST: for tracking group name of User
                print("TEST LOG: USERTYPE-- " + request.user.groups.all()[0].name)
                return render(request, 'home.html', {})

            else:
                hasUsertype = False

        if hasUsertype == False:
            # ERROR: 404, "User not found."
            return redirect('login')

    except ObjectDoesNotExist:
        print('ERROR: 404, User not found.')
    return render(request, 'home.html', {})

def error(request):
    return render(request, 'partials/error.html', {})
    

from django.shortcuts import render, redirect

# for storing error messages
from django.contrib import messages

# for handling try-catch exceptions
from django.core.exceptions import ObjectDoesNotExist

# for User login validation
from django.contrib.auth.models import auth, User, Group

# for ending User session
from django.contrib.auth import logout

def debug(m):
    print("------------------------[DEBUG]------------------------")
    print(m)
    print("-------------------------------------------------------")

# LOGIN function
def login(request):
""""
Login function for SIDC users. 
Error handling for:
- Incorrect username and/or password
- Empty either/or submitted fields 
- Attempted user login but no belonging to a usertype/Group (e.g., admin)
"""
    if request.method == 'POST':
        uname = request.POST['user-name']
        password = request.POST['user-pass']

        user = auth.authenticate(username=uname,password=password)
    
        if user is not None: # User exists, next check if User belongs to a Group.
            auth.login(request, user)
            
            # (TRY-CATCH) for checking if User belongs in a Group
            try: 
                userGroup = request.user.groups.all()[0].name
            except IndexError: # for handling list index exception
                # (ERROR) User has no group; None value
                debug("in LOGIN ERROR: Unauth access")
                messages.error(request, "Unauthorized access. Please login.", extra_tags='login')
                return redirect('login')  
            else:
                hasUsertype = False

                if userGroup is not None: 
                    for g in Group.objects.filter(): # in list of Group names, find group of the User
                        if g.name == userGroup:
                            hasUsertype = True
                            # (SUCCESS) User has group, redirect to Home page.
                            print("TEST LOG: USERTYPE-- " + request.user.groups.all()[0].name)
                            return redirect("home")

                    if not hasUsertype:
                        # (ERROR) User came from attempted login, but with no usertype
                        debug("in LOGIN ERROR: Unauth access")
                        messages.error(request, "Unauthorized access. Please login.", extra_tags='login')
                        return redirect('login')  
        else:
            # (ERROR) User inputs have empty fields or are incorrect.
            debug("in LOGIN ERROR: Incorrect credentials")
            messages.error(request, "Incorrect credentials. Please try again.", extra_tags='login')
            return redirect('login')
            
    return render(request, 'login.html', {})



def home_view(request):
    print("TEST LOG: in Home view/n")
    return render(request, 'home.html', {})

# LOGOUT function
def logout_view(request):
    logout(request)
    
    print("TEST LOG: User signed out.")
    return redirect('login')

def error(request):
    return render(request, 'partials/error.html', {})
    

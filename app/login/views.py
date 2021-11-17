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
    if request.method == 'POST':
        uname = request.POST['user-name']
        password = request.POST['user-pass']

        user = auth.authenticate(username=uname,password=password)
    
        if user is not None:
            if user.is_active: # successful login, proceed to Home view
                auth.login(request, user)
                return redirect('home')
            else:
                error = {'errCode': 404, 
                    'errMessage': 'Unauthorized access. Please login.'
                }
                debug("in LOGIN ERROR: Unauth access")
                return render(request, 'login.html', error)

        else:
            error = {'errCode': 404, 
                'errMessage': 'Incorrect credentials. Please try again.'
            }
            debug("in LOGIN ERROR: Incorrect credentials")
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
        userGroup = request.user.groups.all()[0].name
    except IndexError:
        # (ERROR) User has no group; None value
        error = {'errCode': 404, 
            'errMessage': 'Unauthorized access. Please login.'
        }
        debug("in LOGIN ERROR: Unauth access")
        return render(request, 'login.html', error)   

    else:
        hasUsertype = False

        if userGroup is not None: 
            for g in Group.objects.filter(): # in list of Group names, find group of the User
                if g.name == userGroup:
                    hasUsertype = True
                    # TEST: for tracking group name of User
                    print("TEST LOG: USERTYPE-- " + request.user.groups.all()[0].name)
                    return render(request, 'home.html', {})

            if not hasUsertype:
                # (ERROR) User came from attempted login, but with no usertype
                error = {'errCode': 404, 
                    'errMessage': 'Unauthorized access. Please login.'
                }
                debug("in LOGIN ERROR: Unauth access")
                return render(request, 'login.html', error)
        else:
            # (ERROR) User has no group; None value
            error = {'errCode': 404, 
                'errMessage': 'Unauthorized access. Please login.'
            }
            debug("in LOGIN ERROR: Unauth access")
            return render(request, 'login.html', error)
        
    # except ObjectDoesNotExist:
    return redirect('login')

def error(request):
    return render(request, 'partials/error.html', {})
    

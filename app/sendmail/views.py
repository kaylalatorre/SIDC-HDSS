from django.shortcuts import render
# for sending email
from django.core.mail import send_mail


# Create your views here.

# Send account details to system user
# TODO: Where to connect this function? When will it be triggered?
def index(request):
    # if request.method == "POST":
    #     mssg_name = request.POST['<name of user>']
    #     mssg_email = request.POST['<email of user>']
    #     message = request.POST['<mssg to be sent>']
        # Send the email
    send_mail(
        "[SIDC] Account Verification", # subject
        "Hello email recipient. This is a message.", # message
        'training.tvh@gmail.com', # From email
        ['gerajem293@jesdoit.com'], # To email
        fail_silently=False
    )
    return render('send/index.html')
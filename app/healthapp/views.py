from django.shortcuts import render

# Create your views here.

def hogsHealth(request):
    return render(request, 'healthtemp/hogs-health.html', {})

def selectedHogsHealth(request):
    return render(request, 'healthtemp/selected-hogs-health.html', {})
from django.shortcuts import render

# Farms Management Module Views

def farms(request):
    return render(request, 'farmstemp/farms.html', {})
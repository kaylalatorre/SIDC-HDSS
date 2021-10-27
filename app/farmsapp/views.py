from django.shortcuts import render

# Farms Management Module Views

## Farms table for all users except Technicians
def farms(request):
    return render(request, 'farmstemp/farms.html', {})

## Add Farms
def addFarm(request):
    return render(request, 'farmstemp/add-farm.html', {})


<<<<<<< HEAD
=======
from django.shortcuts import render

# Farms Management Module Views

## Farms table for all users except Technicians
def farms(request):
    return render(request, 'farmstemp/farms.html', {})

## Add Farms
def addFarm(request):
    return render(request, 'farmstemp/add-farm.html', {})

>>>>>>> fcac6f08812a7cf37d5cad0e42d903fd8cd2f13a

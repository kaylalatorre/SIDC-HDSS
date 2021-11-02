from django.shortcuts import render
from farmsapp.models import Farm
# Farms Management Module Views

def farms(request):
    for f in Farm.objects.all().values_list():
        print(f[0])

    return render(request, 'farmstemp/farms.html', {}) ## Farms table for all users except Technicians

def addFarm(request):
    return render(request, 'farmstemp/add-farm.html', {})

def biosecurity(request):
    return render(request, 'farmstemp/biosecurity.html', {})

def addChecklist(request):
    return render(request, 'farmstemp/add-checklist.html', {})

def addActivity(request):
    return render(request, 'farmstemp/add-activity.html', {})
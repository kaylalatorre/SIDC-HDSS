from django.shortcuts import render

# Create your views here.

def hogsHealth(request):
    return render(request, 'healthtemp/hogs-health.html', {})

def selectedHogsHealth(request):
    return render(request, 'healthtemp/selected-hogs-health.html', {})

def hogsMortality(request):
    return render(request, 'healthtemp/rep-hogs-mortality.html', {})

def symptomsReported(request):
    return render(request, 'healthtemp/rep-symptoms-reported.html', {})

def healthSymptoms(request):
    return render(request, 'healthtemp/health-symptoms.html', {})

def selectedHealthSymptoms(request):
    return render(request, 'healthtemp/selected-health-symptoms.html', {})

def addCase(request):
    return render(request, 'healthtemp/add-case.html', {})
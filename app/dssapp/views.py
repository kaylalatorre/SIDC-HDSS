# for page redirection, server response
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, response

# for storing success and error Django messages
from django.contrib import messages

# for Model imports
from django.contrib.auth.models import User
from farmsapp.models import (
    Farm, Area, Hog_Raiser, Farm_Weight, 
    Mortality, Hog_Symptoms, Mortality_Form, 
    Pigpen_Group, Pigpen_Row)

# for Model CRUD query functions
from django.db.models.expressions import F, Value
from django.db.models import Q
# from django.forms.formsets import formset_factory
from django.db import connections

# for date and time fields in Models
from datetime import date, datetime, timezone, timedelta
from django.utils.timezone import (
    make_aware, # for date and time fields in Models
    now, # for getting date today
    localtime # for getting date today
) 

# for AJAX functions
from django.http import JsonResponse
from django.core import serializers
import json

# for date and time fields in Models
from datetime import date, datetime, timezone, timedelta
from django.utils.timezone import (
    make_aware, # for date and time fields in Models
    now, # for getting date today
    localtime # for getting date today
) 

def debug(m):
    """
    For debugging purposes

    :param m: The message
    :type m: String
    """
    print("------------------------[DEBUG]------------------------")
    print(m)
    print("-------------------------------------------------------")

# (Module 3) Disease Monitoring view functions

def diseaseMonitoring(request):

    return render(request, 'dsstemp/rep-disease-monitoring.html', { })

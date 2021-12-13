# for page redirection, server response
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, response

# for storing success and error Django messages
from django.contrib import messages

# for Model imports
from django.contrib.auth.models import User
from farmsapp.models import Farm, Area, Hog_Raiser, Farm_Weight, Mortality, Hog_Symptoms

# for Model CRUD query functions
from django.db.models.expressions import F, Value
from django.db.models import Q
# from django.forms.formsets import formset_factory


def debug(m):
    """
    For debugging purposes

    :param m: The message
    :type m: String
    """
    print("------------------------[DEBUG]------------------------")
    print(m)
    print("-------------------------------------------------------")

# (Module 2) Hogs Health view functions

def count_activeIncidents(farmID):
    total_active = 0

    # symptomQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).count()

    return total_active

def compute_MortRate(farmID):
    """
    Computes for the mortality rate of a Farm.
    mortality % = num_toDate / num_begInv
    """
    mortality_rate = 0

    mortQry = Mortality.objects.filter(ref_farm_id=farmID)

    if mortQry.exists():
        m = mortQry.first()

        mortality_rate = (m.num_toDate / m.num_begInv) * 100

    return mortality_rate

def hogsHealth(request):
    """
    Gets Hogs Health records for all Farms in all Areas due to no selected filters.

    (1) Farm details
        - farm code, raiser full name, area, technician assigned (?), num pigs
    (2) Farm Weight
        - ave_startWeight, ave_currWeight
    (3) Mortality
        - mortality_rate (mortality % = num_toDate / num_begInv)
    (4) Hog Symptoms
        - symptoms_reported, active_symptoms
    """

    # (1) Farm details 
    qry = Farm.objects.select_related('hog_raiser', 'area', 'farm_weight', 'hog_symptoms').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        farm_area = F("area__area_name"),
        symptomsID = F("hog_symptoms__id"),
        ave_currWeight = F("farm_weight__ave_weight"),
        is_starterWeight = F("farm_weight__is_starter")
        ).values(
            "id",
            "fname",
            "lname", 
            "farm_area",
            "total_pigs",
            "last_updated",
            "symptomsID",
            "ave_currWeight",
            "is_starterWeight"
            )
    debug(qry)

    if not qry.exists(): 
        messages.error(request, "No hogs health records found.", extra_tags="view-hogsHealth")
        return render(request, 'healthtemp/hogs-health.html', {})

    farmsData = []
    total_pigs = 0
    for f in qry:

        farmID = f["id"]

        # for computing Mortality %
        mortality_rate = compute_MortRate(farmID)

        # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
        total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).count()

        farmObject = {
            "code":  str(f["id"]),
            "raiser": " ".join((f["fname"],f["lname"])),
            "area": str(f["farm_area"]),
            "pigs": str(f["total_pigs"]),
            "updated": f["last_updated"],
            "ave_currWeight": str(f["ave_currWeight"]),
            "is_starterWeight": str(f["is_starterWeight"]),

            "mortality_rate": mortality_rate,
            "total_incidents": total_incidents,
        }
        farmsData.append(farmObject)

        total_pigs += f["total_pigs"]

    debug(farmsData)

    

    # TODO: for "Active Incidents" column
    # Naka-FK hogs symptoms sa farm, so para siyang 'yung intbio and extbio na 
    # 'yung latest ang naka-FK (so lahat ng True sa naka-FK na record, ayun 'yung Active Symptoms)
    # 



    return render(request, 'healthtemp/hogs-health.html', {"farmList": farmsData})

def selectedHogsHealth(request):
    return render(request, 'healthtemp/selected-hogs-health.html', {})

def hogsMortality(request):
    return render(request, 'healthtemp/rep-hogs-mortality.html', {})

def incidentsReported(request):
    return render(request, 'healthtemp/rep-incidents-reported.html', {})

def healthSymptoms(request):
    return render(request, 'healthtemp/health-symptoms.html', {})

def selectedHealthSymptoms(request):
    return render(request, 'healthtemp/selected-health-symptoms.html', {})

def addCase(request):
    return render(request, 'healthtemp/add-case.html', {})
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


def compute_MortRate(farmID):
    """
    Computes for the mortality rate of a Farm.
    mortality % = num_toDate / num_begInv
    """
    mortality_rate = 0

    # Get latest Mortality record of the Farm
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).order_by('-mortality_date')

    if mortQry.exists():
        m = mortQry.first()

        mortality_rate = (m.num_toDate / m.num_begInv) * 100

    return round(mortality_rate, 2)

# for Asst. Manager view Hogs Health
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
        - incidents reported, active incidents
    """

    # (1) Farm details 
    qry = Farm.objects.select_related('hog_raiser', 'area', 'farm_weight').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        farm_area = F("area__area_name"),
        ave_currWeight = F("farm_weight__ave_weight")
        # is_starterWeight = F("farm_weight__is_starter")
        ).values(
            "id",
            "fname",
            "lname", 
            "farm_area",
            "total_pigs",
            "last_updated",
            "ave_currWeight"
            # "is_starterWeight"
            ).order_by("id")
    debug(qry)

    if not qry.exists(): 
        messages.error(request, "No hogs health records found.", extra_tags="view-hogsHealth")
        return render(request, 'healthtemp/hogs-health.html', {})

    farmsData = []
    total_pigs = 0
    total_incidents = 0
    total_active = 0
    for f in qry:

        farmID = f["id"]

        # for computing Mortality %
        mortality_rate = compute_MortRate(farmID)

        # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
        total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).count()

        # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
        total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(report_status="ACTIVE").count()

        farmObject = {
            "code":  str(f["id"]),
            "raiser": " ".join((f["fname"],f["lname"])),
            "pigs": str(f["total_pigs"]),
            "updated": f["last_updated"],
            "ave_currWeight": str(f["ave_currWeight"]),
            # "is_starterWeight": str(f["is_starterWeight"]),

            "mortality_rate": mortality_rate,
            "total_incidents": total_incidents,
            "total_active": total_active,
        }
        farmsData.append(farmObject)

        total_pigs += f["total_pigs"]
    # debug(farmsData)

    
    return render(request, 'healthtemp/hogs-health.html', {"farmList": farmsData})

def selectedHogsHealth(request):
    return render(request, 'healthtemp/selected-hogs-health.html', {})

def hogsMortality(request):
    return render(request, 'healthtemp/rep-hogs-mortality.html', {})

def symptomsReported(request):
    return render(request, 'healthtemp/rep-symptoms-reported.html', {})


# for Technician view Hogs Health
def healthSymptoms(request):
    """
    Gets Hogs Health records for all Farms within Technician area.

    (1) Farm details
        - farm code, raiser full name, num pigs
    (2) Farm Weight
        - ave_startWeight, ave_currWeight
    (3) Mortality
        - mortality_rate (mortality % = num_toDate / num_begInv)
    (4) Hog Symptoms
        - incidents reported, active incidents
    """

    # Get all Areas assigned to logged-in technician User
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all()
    print("TEST LOG areaQry: " + str(areaQry))

    # array to store all farms under each area
    farmsData = []

    for area in areaQry :
        # print(str(area.id) + str(area.area_name))

        # (1) filter by area, then collect details for each Farm 
        qry = Farm.objects.filter(area_id=area.id).select_related('hog_raiser','farm_weight').annotate(
            fname=F("hog_raiser__fname"), 
            lname=F("hog_raiser__lname"), 
            ave_currWeight = F("farm_weight__ave_weight")
            # is_starterWeight = F("farm_weight__is_starter")
            ).values(
                "id",
                "fname",
                "lname", 
                "total_pigs",
                "last_updated",
                "ave_currWeight"
                # "is_starterWeight"
                ).order_by("id")
        # debug(qry)
        
        total_pigs = 0
        total_incidents = 0
        total_active = 0
        for f in qry:

            farmID = f["id"]

            # for computing Mortality %
            mortality_rate = compute_MortRate(farmID)

            # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
            total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).count()

            # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
            total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(report_status="ACTIVE").count()

            farmObject = {
                "code":  str(f["id"]),
                "raiser": " ".join((f["fname"],f["lname"])),
                "pigs": str(f["total_pigs"]),
                "updated": f["last_updated"],
                "ave_currWeight": str(f["ave_currWeight"]),
                # "is_starterWeight": str(f["is_starterWeight"]),

                "mortality_rate": mortality_rate,
                "total_incidents": total_incidents,
                "total_active": total_active,
            }
            farmsData.append(farmObject)

            total_pigs += f["total_pigs"]
        debug("-- farmsData ---")
        debug(farmsData)


    # (ERROR) for checking technician Areas that have no assigned Farms
    if not farmsData: 
        messages.error(request, "Hogs health record/s not found.", extra_tags="view-healthSymp")
        return render(request, 'farmstemp/biosecurity.html', {})


    return render(request, 'healthtemp/health-symptoms.html', {"farmList": farmsData})

def selectedHealthSymptoms(request):
    return render(request, 'healthtemp/selected-health-symptoms.html', {})

def addCase(request):
    return render(request, 'healthtemp/add-case.html', {})
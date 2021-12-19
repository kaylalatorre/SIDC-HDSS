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

# for AJAX functions
from django.http import JsonResponse
from django.core import serializers
import json

# for string regex
import re

# for Forms
from farmsapp.forms import (
    MortalityForm
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

# (Module 2) Hogs Health view functions


def compute_MortRate(farmID, mortalityID):
    """
    Helper function that computes for the mortality rate of a Farm.
    mortality % = num_toDate / num_begInv
    """
    mortality_rate = 0

    # compute mortality % with the given farmID (latest mortality record in a Farm)
    if farmID is not None:
        # Get latest Mortality record of the Farm
        mortQry = Mortality.objects.filter(ref_farm_id=farmID).order_by('-mortality_date')

        if mortQry.exists():
            m = mortQry.first()

            mortality_rate = (m.num_toDate / m.num_begInv) * 100

    # compute mortality % with the given mortalityID
    if mortalityID is not None:
        mortObj = Mortality.objects.filter(id=mortalityID).first()

        if mortObj is not None:
            mortality_rate = (mortObj.num_toDate / mortObj.num_begInv) * 100

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
    # for list of Areas in checkbox filter
    areaQry = Area.objects.only("area_name").all()

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
    # debug(qry)

    if not qry.exists(): 
        messages.error(request, "No hogs health records found.", extra_tags="view-hogsHealth")
        return render(request, 'healthtemp/hogs-health.html', {"areaList": areaQry})

    farmsData = []
    total_pigs = 0
    total_incidents = 0
    total_active = 0
    for f in qry:

        farmID = f["id"]

        # for computing Mortality %
        mortality_rate = compute_MortRate(farmID, None)

        # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
        total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).count()

        # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
        total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(report_status="Active").count()

        farmObject = {
            "code":  f["id"],
            "raiser": " ".join((f["fname"],f["lname"])),
            "area": f["farm_area"],
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


    return render(request, 'healthtemp/hogs-health.html', {"areaList": areaQry, "farmList": farmsData})


def selectedHogsHealth(request, farmID):
    """
    Displays information of selected hogs health record for assistant manager

    :param farmID: PK of selected farm
    :type farmID: string
    """

    debug("TEST LOG: in selectedHogsHealth()/n")
    debug("farmID -- " + str(farmID))

    # (1) get farm based on farmID; get related data from hog_raiser, area, farm_weight
    selectFarm = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'farm_weight').annotate(
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
            ).first()
    # debug(qry)

    if selectFarm is None: 
        messages.error(request, "Hogs health record not found.", extra_tags="selected-hogsHealth")
        return render(request, 'healthtemp/selected-hogs-health.html', {})


    total_incidents = 0
    total_active = 0

    # for computing Mortality %
    mortality_rate = compute_MortRate(farmID, None)

    # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
    total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).count()

    # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
    total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(report_status="Active").count()

    farmObject = {
        "code":  farmID,
        "raiser": " ".join((selectFarm["fname"], selectFarm["lname"])),
        "area": selectFarm["farm_area"],
        "pigs": selectFarm["total_pigs"],
        "updated": selectFarm["last_updated"],
        "ave_currWeight": selectFarm["ave_currWeight"],
        # "is_starterWeight": str(f["is_starterWeight"]),

        "mortality_rate": mortality_rate,
        "total_incidents": total_incidents,
        "total_active": total_active,
    }


    # (2.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).only(
        'date_filed', 
        'report_status',
        'num_pigs_affected').order_by("id").all()

    # (2.2) Incidents Reported (symptoms list)
    symptomsList = Hog_Symptoms.objects.filter(ref_farm_id=farmID).values(
            'high_fever'        ,
            'loss_appetite'     ,
            'depression'        ,
            'lethargic'         ,
            'constipation'      ,
            'vomit_diarrhea'    ,
            'colored_pigs'      ,
            'skin_lesions'      ,
            'hemorrhages'       ,
            'abn_breathing'     ,
            'discharge_eyesnose',
            'death_isDays'      ,
            'death_isWeek'      ,
            'cough'             ,
            'sneeze'            ,
            'runny_nose'        ,
            'waste'             ,
            'boar_dec_libido'   ,
            'farrow_miscarriage',
            'weight_loss'       ,
            'trembling'         ,
            'conjunctivitis').order_by("id").all()

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidentQry, symptomsList)


    # (3.1) Mortality Records
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).order_by("id").all()

    mortality_rate = 0
    mRateList = [] 
    # (3.2) Mortality % per record
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList)
    
    return render(request, 'healthtemp/selected-hogs-health.html', {"farm": farmObject, 
                                                                    "incident_symptomsList": incident_symptomsList,
                                                                    "mortalityList": mortalityList})



def hogsMortality(request):
    return render(request, 'healthtemp/rep-hogs-mortality.html', {})

def incidentsReported(request):
    return render(request, 'healthtemp/rep-incidents-reported.html', {})


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
    areaQry = Area.objects.filter(tech_id=techID).all().order_by('id')

    # array to store all farms under each area
    farmsData = []

    for area in areaQry :
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
            mortality_rate = compute_MortRate(farmID, None)

            # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
            total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).count()

            # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
            total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(report_status="Active").count()

            farmObject = {
                "code":  f["id"],
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
        # debug("-- farmsData ---")
        # debug(farmsData)


    # (ERROR) for checking technician Areas that have no assigned Farms
    if not farmsData: 
        messages.error(request, "Hogs health record/s not found.", extra_tags="view-healthSymp")
        return render(request, 'healthtemp/health-symptoms.html', {})


    return render(request, 'healthtemp/health-symptoms.html', {"farmList": farmsData})

def selectedHealthSymptoms(request, farmID):
    """
    Displays information of selected hogs health record for Technician user.

    :param farmID: PK of selected farm
    :type farmID: string
    """

    debug("TEST LOG: in selectedHealthSymptoms()")
    debug("farmID -- " + str(farmID))


    # (1.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).only(
        'date_filed', 
        'report_status',
        'num_pigs_affected').order_by("id").all()

    # (1.2) Incidents Reported (symptoms list)
    symptomsList = Hog_Symptoms.objects.filter(ref_farm_id=farmID).values(
            'high_fever'        ,
            'loss_appetite'     ,
            'depression'        ,
            'lethargic'         ,
            'constipation'      ,
            'vomit_diarrhea'    ,
            'colored_pigs'      ,
            'skin_lesions'      ,
            'hemorrhages'       ,
            'abn_breathing'     ,
            'discharge_eyesnose',
            'death_isDays'      ,
            'death_isWeek'      ,
            'cough'             ,
            'sneeze'            ,
            'runny_nose'        ,
            'waste'             ,
            'boar_dec_libido'   ,
            'farrow_miscarriage',
            'weight_loss'       ,
            'trembling'         ,
            'conjunctivitis').order_by("id").all()


    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidentQry, symptomsList)


    # (2) Mortality Records
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).order_by("id").all()

    mortality_rate = 0
    mRateList = [] 
    # (3.2) Mortality % per record
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList)

    return render(request, 'healthtemp/selected-health-symptoms.html', {"farm_code": farmID, "incident_symptomsList": incident_symptomsList,
                                                                        "mortalityList": mortalityList})


def edit_incidStat(request, incidID):
    """
    (POST-AJAX) For updating report_status based on incident ID
    """

    if request.is_ajax and request.method == 'POST':

        debug("TEST LOG: in edit_incidStat()/n")

        # Get report status from sent AJAX post data
        select_status = request.POST.get("selectStat")
        debug("select_status -- " + select_status)

        # search if Incident exists in db
        incidentObj = Hog_Symptoms.objects.filter(id=incidID).first()

        if incidentObj is not None:
            incidentObj.report_status = select_status
            incidentObj.save()

            debug("(SUCCESS) Incident status successfully updated!")

            # Get updated status from db
            updatedStat = incidentObj.report_status
            return JsonResponse({"updated_status": updatedStat, "status_code":"200"}, status=200)

        else:
            return JsonResponse({"error": "Incident record not found", "status_code":"400"}, status=400)

    # # Serialize dictionary
    # jsonStr = json.dumps(bioDict)
    # return JsonResponse({"instance": jsonStr, "status_code":"200"}, status=200)

    return JsonResponse({"error": "not an AJAX post request"}, status=400)



def addCase(request):
    return render(request, 'healthtemp/add-case.html', {})

def addMortality(request):
    """
    - Redirect to Add Mortality Page and render corresponding Django form
    - Add new mortality record to database and connect to new instance of Mortality Form (as FK)
    - Save details to mortality and add FK of selected farm table
    - Django forms will first check the validity of input (based on the fields within models.py)

    """
    
    # generate series number
    series = int(101010)

    # get all farms under current technician
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all().order_by('id')

    # array to store all farms under each area
    techFarms = []

    for area in areaQry :
        # collect the corresponding hog raiser details for each farm 
        techFarmQry  = Farm.objects.filter(area_id=area.id).values("id").order_by('id').all()

        # pass all data into an array
        for farm in techFarmQry:
            farmObject = {
                "id": farm["id"],
            }
            techFarms.append(farmObject)

    if request.method == 'POST':
        print("TEST LOG: Add Mortality has POST method") 
        print(request.POST)

        mortalityForm = MortalityForm(request.POST)

        if mortalityForm.is_valid():
            print("TEST LOG: mortalityForm is valid")

        else:
            print("TEST LOG: mortalityForm is not valid")
            
            print(mortalityForm.errors.as_text)
            print(mortalityForm.non_field_errors().as_text)

            formError = str(mortalityForm.non_field_errors().as_text)
            print(re.split("\'.*?",formError)[1])

            messages.error(request, "Error adding mortality record. " + str(re.split("\'.*?",formError)[1]), extra_tags='add-activity')

    else:
        print("TEST LOG: Add Activity is not a POST method")

        mortalityForm = MortalityForm()
    
    return render(request, 'healthtemp/add-mortality.html', {'series' : series, 'farms' : techFarms, 'mortalityForm' : mortalityForm})
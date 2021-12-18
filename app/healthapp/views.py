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
    else:

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
        debug(farmsData)


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
        "code":  int(farmID),
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
    
    # for getting length of Incident records
    total_incidents = incidentQry.count()
    # debug("total_incidents -- " + str(total_incidents))

    return render(request, 'healthtemp/selected-hogs-health.html', {"total_incidents": total_incidents, "farm": farmObject, 
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
        debug("-- farmsData ---")
        debug(farmsData)


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

    debug("TEST LOG: in selectedHealthSymptoms()/n")
    debug("farmID -- " + str(farmID))


    # (1.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).only(
        'date_filed',
        'date_updated', 
        'report_status',
        'num_pigs_affected').order_by("id").all()

    # for checking if Incident record is "RESOLVED" and exceeds 1 day
    editList = []
    for s in incidentQry:

        # get date diff of date_filed from date_updated
        sDateDiff = datetime.now(timezone.utc) - s.date_updated
        # debug("sDateDiff.days -- " + str(sDateDiff.days))
        
        isEditable = True
        # set as false if date diff exceeds 1 day
        if s.report_status == "Resolved" and sDateDiff.days > 1:
            isEditable = False
            
        editList.append(isEditable)


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
    incident_symptomsList = zip(incidentQry, symptomsList, editList)


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

    # for getting length of Incident records
    total_incidents = incidentQry.count()

    return render(request, 'healthtemp/selected-health-symptoms.html', {"total_incidents": total_incidents, "farm_code": int(farmID), "incident_symptomsList": incident_symptomsList,
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

        # get date diff of date_filed from date_updated
        repDateDiff = datetime.now(timezone.utc) - incidentObj.date_updated
        debug("repDateDiff.days -- " + str(repDateDiff.days))

        if incidentObj is not None:
            # (ERROR 1) if select_status is ACTIVE & db_status is PENDING 
            if select_status == "Active" and incidentObj.report_status == "Pending":
                return JsonResponse({"error": "Cannot set [PENDING] report status back to [ACTIVE].", "status_code":"400"}, status=400)

            # (ERROR 2) if db_status is RESOLVED & exceeds 1 day
            # Note: already handled in selectedHealthSymptoms()

            else: # (SUCCESS) No restrictions, can edit report_status
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



def addCase(request, farmID):
    return render(request, 'healthtemp/add-case.html', {"farmID": farmID})

# (POST) AJAX function for adding a Symptoms list under a Farm
def post_addCase(request, farmID):
    print("TEST LOG: in post_addCase/n")

    if request.method == "POST":
        
        # Get farmID from URL param and check if farmID exists
        if Farm.objects.filter(id=farmID).exists():

            debug("in POST addCase /n: farmID -- " + str(farmID))
            
            # get num_pigs & symptoms Array from AJAX post 
            num_pigsAffected = request.POST.get("num_pigsAffected")

            sList = request.POST.getlist("symptomsArr[]")
            symptomsArr = []
            for s in sList:
                if s == "true":
                    symptomsArr.append(True)
                else:
                    symptomsArr.append(False)
            

            # Array length must be 22 for the fields in Symptoms list.
            debug("sympArr len(): " + str(len(symptomsArr)))
            debug("num_pigsAffected: " + str(num_pigsAffected))

            debug(symptomsArr);

            if len(symptomsArr) > 0 and int(num_pigsAffected) > 0: # (SUCCESS) Symptoms list is complete, proceed to add in db

                # init Hog_Symptoms and Farm models
                incidObj = Hog_Symptoms() 
                farmQuery = Farm.objects.get(pk=farmID)

                # Put num_pigs, symptoms list into Hog_Symptoms model
                incidObj.ref_farm           = farmQuery
                incidObj.num_pigs_affected  = num_pigsAffected
                incidObj.high_fever         = symptomsArr[0]
                incidObj.loss_appetite      = symptomsArr[1]
                incidObj.depression         = symptomsArr[2]
                incidObj.lethargic          = symptomsArr[3]
                incidObj.constipation       = symptomsArr[4]
                incidObj.vomit_diarrhea     = symptomsArr[5]
                incidObj.colored_pigs       = symptomsArr[6]
                incidObj.skin_lesions       = symptomsArr[7]
                incidObj.hemorrhages        = symptomsArr[8]
                incidObj.abn_breathing      = symptomsArr[9]
                incidObj.discharge_eyesnose = symptomsArr[10]
                incidObj.death_isDays       = symptomsArr[11]
                incidObj.death_isWeek       = symptomsArr[12]
                incidObj.cough              = symptomsArr[13]
                incidObj.sneeze             = symptomsArr[14]
                incidObj.runny_nose         = symptomsArr[15]
                incidObj.waste              = symptomsArr[16]
                incidObj.boar_dec_libido    = symptomsArr[17]
                incidObj.farrow_miscarriage = symptomsArr[18]
                incidObj.weight_loss        = symptomsArr[19]
                incidObj.trembling          = symptomsArr[20]
                incidObj.conjunctivitis     = symptomsArr[21]

                # for updating pk counter of Hog_Symptoms
                # References: 
                # - https://stackoverflow.com/questions/9108833/postgres-autoincrement-not-updated-on-explicit-id-inserts
                # - https://newbedev.com/duplicate-key-value-violates-unique-constraint-detail-key-user-id-1-already-exists-code-example
                query = "SELECT setval('farmsapp_hog_symptoms_id_seq', (SELECT MAX(id) from farmsapp_hog_symptoms))"
                cursor = connections['default'].cursor()
                cursor.execute(query) 
                row = cursor.fetchone()

                # save data to table
                incidObj.save()
                incidObj.date_filed = incidObj.date_updated
                incidObj.save()

                # Format time to be passed on message.success
                ts = incidObj.date_filed
                df = ts.strftime("%m/%d/%Y, %H:%M")
                debug(incidObj.date_filed)
                

                debug("(SUCCESS) Incident report added.")
                # (SUCCESS) Incident has been added. Properly redirect to selected view page
                messages.success(request, "Incident report made on " + df + " has been successfully added!", extra_tags='add-incidCase')
                return JsonResponse({"status_code":"200"}, status=200)
        
            else:
                # (ERROR) No selected input/s for Incident Case.
                debug("ERROR: No selected input/s for Incident Case.")
                messages.error(request, "No selected input/s for Incident Case.", extra_tags='add-incidCase')
                return JsonResponse({"error": "No selected input/s for Incident Case.", "status_code":"400"}, status=400)
        else:
            # (ERROR) Invalid farmID
            debug("ERROR: Invalid/None-type farmID from parameter.")
            messages.error(request, "Farm record not found.", extra_tags='add-incidCase')
            # return redirect('/selected-health-symptoms'+ farmID)
            return JsonResponse({"error": "Farm record not found.", "status_code":"400"}, status=400)

    else:
        # (ERROR) not an AJAX Post request
        messages.error(request, "No selected input/s for Incident Case.", extra_tags='add-incidCase')
        # return redirect('/add-case/' + farmID)
        return JsonResponse({"error": "No selected input/s for Incident Case.", "status_code":"400"}, status=400)


def addMortality(request):
    return render(request, 'healthtemp/add-mortality.html', {})
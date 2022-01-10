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

# # for string regex
# import re

# for Forms
from farmsapp.forms import (
    MortalityForm,
    WeightForm
)

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

# (Module 2) Hogs Health view functions


def compute_MortRate(farmID, mortalityID):
    """
    Helper function that computes for the mortality rate of a Farm.
    mortality % = num_toDate / num_begInv
    """
    mortality_rate = 0.0

    # compute mortality % with the given farmID (latest mortality record in a Farm)
    if farmID is not None:
        # get latest Pigpen version
        latestPP = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()

        # Get latest Mortality record of the Farm (w Pigpen filter)
        mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=latestPP.id).filter(is_approved=True).order_by('-mortality_date')

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
        - average starter and fattener
    (3) Mortality
        - mortality_rate (mortality % = num_toDate / num_begInv)
    (4) Hog Symptoms
        - incidents reported, active incidents
    """
    # for list of Areas in checkbox filter
    areaQry = Area.objects.only("area_name").all()

    # (1) Farm details 
    qry = Farm.objects.select_related('hog_raiser', 'area').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        farm_area = F("area__area_name"),
        ).values(
            "id",
            "fname",
            "lname", 
            "farm_area",
            "total_pigs",
            "last_updated",
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
            start_weight = 0.0
            end_weight   = 0.0

            farmID = f["id"]

            # get latest Pigpen version
            latestPP = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()

            # get current starter and fattener weights
            s_weightQry = Farm_Weight.objects.filter(ref_farm_id=farmID).filter(is_starter=True).order_by("-date_filed").first()
            e_weightQry = Farm_Weight.objects.filter(ref_farm_id=farmID).filter(is_starter=False).order_by("-date_filed").first()

            # error checking for None weight values per Farm
            if s_weightQry is not None:
                start_weight = s_weightQry.ave_weight

            if e_weightQry is not None:
                end_weight = e_weightQry.ave_weight

            # for computing Mortality %
            mortality_rate = compute_MortRate(farmID, None)

            # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
            total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPP.id).count()

            # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
            total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPP.id).filter(report_status="Active").count()

            farmObject = {
                "code":             f["id"],
                "raiser":           " ".join((f["fname"],f["lname"])),
                "area":             f["farm_area"],
                "pigs":             f["total_pigs"],
                "updated":          f["last_updated"],
                "ave_startWeight":  start_weight,
                "ave_endWeight":    end_weight,
                "mortality_rate":   mortality_rate,
                "total_incidents":  total_incidents,
                "total_active":     total_active,
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

    # debug("TEST LOG: in selectedHogsHealth()")
    # debug("farmID -- " + str(farmID))

    # (1) get farm based on farmID; get related data from hog_raiser, area, farm_weight
    selectFarm = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        farm_area = F("area__area_name"),
        ).values(
            "id",
            "fname",
            "lname", 
            "farm_area",
            "total_pigs",
            "last_updated",
            ).first()
    # debug(qry)

    if selectFarm is None: 
        messages.error(request, "Hogs health record not found.", extra_tags="selected-hogsHealth")
        return render(request, 'healthtemp/selected-hogs-health.html', {})

    # collecting all past pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()

    total_incidents = 0
    total_active = 0

    # get current starter and fattener weights acc. to current Pigpen
    latestPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()
    pigpenQry = Pigpen_Group.objects.filter(id=latestPigpen.id).select_related("start_weight").select_related("final_weight").first()

    # debug("pigpenQry.start_weight -- " + str(pigpenQry.start_weight))
    # debug("pigpenQry.final_weight -- " + str(pigpenQry.final_weight))

    # for computing Mortality %
    mortality_rate = compute_MortRate(farmID, None)

    # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
    total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPigpen.id).count()

    # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
    total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(report_status="Active").filter(pigpen_grp_id=latestPigpen.id).count()

    farmObject = {
        "code":  int(farmID),
        "raiser": " ".join((selectFarm["fname"], selectFarm["lname"])),
        "area": selectFarm["farm_area"],
        "pigs": selectFarm["total_pigs"],
        "updated": selectFarm["last_updated"],

        "start_weight": pigpenQry.start_weight,
        "end_weight": pigpenQry.final_weight,

        "mortality_rate": mortality_rate,
        "total_incidents": total_incidents,
        "total_active": total_active,
    }


    # (2.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPigpen.id).only(
        'date_filed', 
        'report_status',
        'num_pigs_affected').order_by("id").all()

    # (2.2) Incidents Reported (symptoms list)
    symptomsList = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPigpen.id).values(
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
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=latestPigpen.id).filter(is_approved=True).select_related(
                    'mortality_form').annotate(series=F("mortality_form__series")).order_by("-mortality_date").all()

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
    total_mortalities = mortQry.count()

    return render(request, 'healthtemp/selected-hogs-health.html', {"total_incidents": total_incidents, "total_mortalities": total_mortalities, "farm": farmObject, "incident_symptomsList": incident_symptomsList,
                                                                    "mortalityList": mortalityList, 'version' : allPigpens, 'selectedPigpen' : latestPigpen })

def selectedHogsHealthVersion(request, farmID, farmVersion):
    """
    Displays information of selected hogs health record for assistant manager

    :param farmID: PK of selected farm
    :type farmID: string

    :param farmVersion: date added of farm version (pigpen group)
    :type farmVersion: string
    """

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

    # collecting all past and selected pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()
    selectedPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).filter(date_added=farmVersion).first()
    
    # get current starter and fattener weights acc. to current Pigpen
    pigpenQry = Pigpen_Group.objects.filter(id=selectedPigpen.id).select_related("start_weight").select_related("final_weight").first()

    total_incidents = 0
    total_active = 0

    # for computing Mortality %
    mortality_rate = compute_MortRate(farmID, None)

    # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
    total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=selectedPigpen.id).count()

    # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
    total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(report_status="Active").filter(pigpen_grp_id=selectedPigpen.id).count()

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
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=selectedPigpen.id).only(
        'date_filed', 
        'report_status',
        'num_pigs_affected').order_by("id").all()

    # (2.2) Incidents Reported (symptoms list)
    symptomsList = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=selectedPigpen.id).values(
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
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=selectedPigpen.id).filter(is_approved=True).select_related(
                    'mortality_form').annotate(series=F("mortality_form__series")).order_by("-mortality_date").all()

    mortality_rate = 0
    mRateList = [] 
    # (3.2) Mortality % per record
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList)

    # for getting length of Incident, Mortality records
    total_incidents = incidentQry.count()
    total_mortalities = mortQry.count()
    # debug("total_incidents -- " + str(total_incidents))

    return render(request, 'healthtemp/selected-hogs-health.html', {"total_incidents": total_incidents, "total_mortalities": total_mortalities, "farm": farmObject, "incident_symptomsList": incident_symptomsList,
                                                                    "mortalityList": mortalityList, 'version' : allPigpens, 'selectedPigpen' : selectedPigpen })


# for Technician view Hogs Health
def healthSymptoms(request):
    """
    Gets Hogs Health records for all Farms within Technician area.

    (1) Farm details
        - farm code, raiser full name, num pigs
    (2) Farm Weight
        - average starter and fattener
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
        qry = Farm.objects.filter(area_id=area.id).select_related('hog_raiser', 'farm_weight').annotate(
            fname=F("hog_raiser__fname"), 
            lname=F("hog_raiser__lname"), 
            ).values(
                "id",
                "fname",
                "lname", 
                "total_pigs",
                "last_updated",
                ).order_by("id")
        # debug(qry)
        
        total_pigs = 0
        total_incidents = 0
        total_active = 0
        for f in qry:
            start_weight = 0.0
            end_weight = 0.0

            farmID = f["id"]

            # get current starter and fattener weights
            s_weightQry = Farm_Weight.objects.filter(ref_farm_id=farmID).filter(is_starter=True).order_by("-date_filed").first()
            e_weightQry = Farm_Weight.objects.filter(ref_farm_id=farmID).filter(is_starter=False).order_by("-date_filed").first()

            # error checking for None weight values per Farm
            if s_weightQry is not None:
                start_weight = s_weightQry.ave_weight

            if e_weightQry is not None:
                end_weight = e_weightQry.ave_weight

            # for computing Mortality %
            mortality_rate = compute_MortRate(farmID, None)

            # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
            total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).count()

            # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
            total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(report_status="Active").count()

            farmObject = {
                "code":             f["id"],
                "raiser":           " ".join((f["fname"],f["lname"])),
                "pigs":             f["total_pigs"],
                "updated":          f["last_updated"],
                "ave_startWeight":  start_weight,
                "ave_endWeight":    end_weight,
                "mortality_rate":   mortality_rate,
                "total_incidents":  total_incidents,
                "total_active":     total_active,
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

    # debug("TEST LOG: in selectedHealthSymptoms()")
    # debug("farmID -- " + str(farmID))

    # collecting all past pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()

    # get latest version of Pigpen
    latestPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()
 
    # get current starter and fattener weights acc. to current Pigpen
    pigpenQry = Pigpen_Group.objects.filter(id=latestPigpen.id).select_related("start_weight").select_related("final_weight").first()

    # (1.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPigpen.id).only(
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
    symptomsList = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPigpen.id).values(
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

    # get current starter and fattener weights acc. to current Pigpen
    pigpenQry = Pigpen_Group.objects.filter(id=latestPigpen.id).select_related("start_weight").select_related("final_weight").first()

    # (2) Mortality Records
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=latestPigpen.id).filter(is_approved=True).select_related(
                    'mortality_form').annotate(series=F("mortality_form__series")).order_by("-mortality_date").all()

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
    total_mortalities = mortQry.count()

    return render(request, 'healthtemp/selected-health-symptoms.html', {"total_incidents": total_incidents, "total_mortalities": total_mortalities, "farm_code": int(farmID),
                                                                        "incident_symptomsList": incident_symptomsList, "mortalityList": mortalityList, 'version' : allPigpens,
                                                                        'selectedPigpen' : latestPigpen, "start_weight": pigpenQry.start_weight, "end_weight": pigpenQry.final_weight })


def selectedHealthSymptomsVersion(request, farmID, farmVersion):
    """
    Displays information of selected hogs health record for Technician user.

    :param farmID: PK of selected farm
    :type farmID: string
    
    :param farmVersion: date added of farm version (pigpen group)
    :type farmVersion: string
    """

    # collecting all past and selected pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()
    selectedPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).filter(date_added=farmVersion).first()

    # get current starter and fattener weights acc. to current Pigpen
    pigpenQry = Pigpen_Group.objects.filter(id=selectedPigpen.id).select_related("start_weight").select_related("final_weight").first()

    # (1.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=selectedPigpen.id).only(
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
    symptomsList = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=selectedPigpen.id).values(
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

    # get current starter and fattener weights acc. to selected Pigpen
    pigpenQry = Pigpen_Group.objects.filter(id=selectedPigpen.id).select_related("start_weight").select_related("final_weight").first()

    # (2) Mortality Records
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=selectedPigpen.id).filter(is_approved=True).select_related(
                    'mortality_form').annotate(series=F("mortality_form__series")).order_by("-mortality_date").all()

    mortality_rate = 0
    mRateList = [] 
    # (3.2) Mortality % per record
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList)

    # for getting length of Incident, Mortality records
    total_incidents = incidentQry.count()
    total_mortalities = mortQry.count()

    return render(request, 'healthtemp/selected-health-symptoms.html', {"total_incidents": total_incidents, "total_mortalities": total_mortalities, "farm_code": int(farmID),
                                                                        "incident_symptomsList": incident_symptomsList, "mortalityList": mortalityList, 'version' : allPigpens,
                                                                        'selectedPigpen' : selectedPigpen, "start_weight": pigpenQry.start_weight, "end_weight": pigpenQry.final_weight })


def edit_incidStat(request, incidID):
    """
    (POST-AJAX) For updating report_status based on incident ID
    :param incidID: PK of selected Incident report
    :type incidID: string
    """

    if request.method == 'POST':

        # debug("TEST LOG: in edit_incidStat()/n")

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

    return JsonResponse({"error": "not an AJAX post request"}, status=400)


def addCase(request, farmID):
    """
    Navigation function for add-case template that also passes farmID based on selected Farm.
    :param farmID: PK of selected farm
    :type farmID: string
    """
    # get current total_pigs in Farm for User input range in no. of pigs affected
    farmQry = Farm.objects.filter(pk=farmID).only("total_pigs").first()

    return render(request, 'healthtemp/add-case.html', {"farmID": farmID, "total_pigs": farmQry.total_pigs})

# (POST) AJAX function for adding a Symptoms list under a Farm
def post_addCase(request, farmID):
    """
    (POST) AJAX function for adding an Incident Case (also known as Symptoms list) under a Farm
    :param farmID: PK of selected farm
    :type farmID: string
    """

    # print("TEST LOG: in post_addCase/n")

    if request.method == "POST":
        
        # get farmID from URL param and check if Farm record exists
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


            if len(symptomsArr) > 0 and int(num_pigsAffected) > 0: # (SUCCESS) Symptoms list is complete, proceed to add in db
                
                # init Hog_Symptoms and Farm models
                incidObj = Hog_Symptoms() 
                farmQry = Farm.objects.get(pk=farmID)

                # Check if no. of pigs in report is w/in total_pigs of Farm record
                if int(num_pigsAffected) <= farmQry.total_pigs: 

                    # Put num_pigs, symptoms list into Hog_Symptoms model
                    incidObj.ref_farm           = farmQry
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

                    # for updating pk counter of Hog_Symptoms, for avoiding duplicate PK error
                    # References: 
                    # - https://stackoverflow.com/questions/9108833/postgres-autoincrement-not-updated-on-explicit-id-inserts
                    # - https://newbedev.com/duplicate-key-value-violates-unique-constraint-detail-key-user-id-1-already-exists-code-example
                    query = "SELECT setval('farmsapp_hog_symptoms_id_seq', (SELECT MAX(id) from farmsapp_hog_symptoms))"
                    cursor = connections['default'].cursor()
                    cursor.execute(query) 
                    row = cursor.fetchone()

                    # add latest Pigpen version as FK
                    latestPP = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()
                    incidObj.pigpen_grp = latestPP

                    # save data to table
                    incidObj.save()
                    incidObj.date_filed = incidObj.date_updated
                    incidObj.save()

                    # Format time to be passed on message.success
                    ts = incidObj.date_filed
                    df = ts.strftime("%m/%d/%Y, %H:%M")
                    # debug(incidObj.date_filed)
                    
                    debug("[death] 11 value -- " + str(symptomsArr[11]) + "// [death] 12 value -- " + str(symptomsArr[12]))

                    debug("(SUCCESS) Incident report added.")
                    # (SUCCESS) Incident has been added. Properly redirect to selected view page
                    # IF death is in the symptoms
                    if symptomsArr[11] == True or symptomsArr[12] == True:
                        messages.success(request, "Incident report made on " + df + " has been successfully added! Death is one of the symptoms reported.", extra_tags='add-incidCase-death')
                    # else
                    else:
                        messages.success(request, "Incident report made on " + df + " has been successfully added!", extra_tags='add-incidCase')
                    
                    return JsonResponse({"status_code":"200"}, status=200)
        
                else: # (ERROR) User input of num_pigs is not w/in total_pigs range
                    debug("ERROR: Input only no. of pigs within total hogs of Farm.")
                    messages.error(request, "Input only no. of pigs within total hogs of Farm.", extra_tags='add-incidCase')
                    return JsonResponse({"error": "Input only no. of pigs within total hogs of Farm.", "status_code":"400"}, status=400)
            
            else: # (ERROR) No selected input/s for Incident Case.
                debug("ERROR: No selected input/s for Incident Case.")
                messages.error(request, "No selected input/s for Incident Case.", extra_tags='add-incidCase')
                return JsonResponse({"error": "No selected input/s for Incident Case.", "status_code":"400"}, status=400)
        
        else: # (ERROR) Invalid farmID
            debug("ERROR: Invalid/None-type farmID from parameter.")
            messages.error(request, "Farm record not found.", extra_tags='add-incidCase')
            return JsonResponse({"error": "Farm record not found.", "status_code":"400"}, status=400)

    else:
        # (ERROR) not an AJAX Post request
        messages.error(request, "No selected input/s for Incident Case.", extra_tags='add-incidCase')
        return JsonResponse({"error": "No selected input/s for Incident Case.", "status_code":"400"}, status=400)


def addMortality(request, farmID):
    """
    - Redirect to Add Mortality Page and render corresponding Django form
    - Add new mortality record to database and connect to new instance of Mortality Form (as FK)
    - Save details to mortality and add FK of selected farm table
    - Django forms will first check the validity of input (based on the fields within models.py)

    farmID - selected farmID passed as parameter
    """
    
    # generate series number
    latestForm = Mortality_Form.objects.last()
    try:
        series = int(latestForm.series) + 1
    except:
        series = 1

    # get today's date
    dateToday = datetime.now(timezone.utc)

    # get all farms under current technician
    techID = request.user.id

    # collected farmID of selected tech farm
    farmQuery = Farm.objects.get(pk=farmID)
    # print(farmQuery.total_pigs)

    # get current Farm version
    farmVersion = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()

    if request.method == 'POST':
        # print("TEST LOG: Add Mortality has POST method") 
        print(request.POST)

        mortalityForm = MortalityForm(request.POST)

        # pass all values into one record in mortalityList
        mortalityList = []
        
        i = 0
        for mortality_date in request.POST.getlist('mortality_date', default=None):
            mortalityObject = {
                "mortality_date" : request.POST.getlist('mortality_date', default=None)[i],
                "num_today" : request.POST.getlist('num_today', default=None)[i],
                "source" : request.POST.getlist('source', default=None)[i],
                "remarks" : request.POST.getlist('remarks', default=None)[i],
            }
            
            mortalityList.append(mortalityObject)
            i += 1

        if mortalityForm.is_valid():

            # create instance of Mortality Form model
            mortality_form = Mortality_Form.objects.create(
                series = series,
                date_added = dateToday,
                mort_tech_id = techID,
                ref_farm = farmQuery,
                pigpen_grp = farmVersion
            )
            mortality_form.save()

            # pass all objects in mortalityList into Mortality model
            x = 0
            for mort in mortalityList:
                mort = mortalityList[x]

                # create new instance of Mortality model
                mortality = Mortality.objects.create(
                    ref_farm = farmQuery,
                    mortality_date = mort['mortality_date'],
                    num_begInv = farmQuery.total_pigs,
                    num_today = mort['num_today'],
                    num_toDate = farmQuery.total_pigs - int(mort['num_today']),
                    source = mort['source'],
                    remarks = mort['remarks'],
                    mortality_form_id = mortality_form.id
                )
            
                print(str(mortality))
                mortality.save()
                x += 1

            # NOTIFY USER (PAIWI MANAGEMENT STAFF) - New Mortality Record has been submitted by Field Technician OR New Mortality Record needs approval
            messages.success(request, "Mortality Record has been sent for approval.", extra_tags='add-mortality')
            return redirect('/health-symptoms')

        else:
            # print("TEST LOG: mortalityForm is not valid")
            # formError = str(mortalityForm.non_field_errors().as_text)
            # print(re.split("\'.*?",formError)[1])

            # messages.error(request, "Error adding mortality record. " + str(re.split("\'.*?",formError)[1]), extra_tags='add-mortality')
            messages.error(request, "Error adding mortality record. " + str(mortalityForm.non_field_errors().as_text), extra_tags='add-mortality')

    else:
        print("TEST LOG: Add Mortality is not a POST method")

        mortalityForm = MortalityForm()
    
    return render(request, 'healthtemp/add-mortality.html', { 'farmID' : farmID, 'series' : series, 'mortalityForm' : mortalityForm, 'num_begInv' : farmQuery.total_pigs})

def selectedMortalityForm(request, mortalityFormID, mortalityDate):
    """
    - Display all mortality rows for the selected mortality form

    mortalityFormID = id value of selected mortality form
    mortalityDate = date_added value of mortality form selected
    """

    # get details of mortality form
    mortFormQuery = Mortality_Form.objects.filter(id=mortalityFormID).first()

    # get latest
    latestForm = Mortality_Form.objects.filter(series=mortFormQuery.series).last()

    # set status of mortality form
    if request.user.groups.all()[0].name == "Paiwi Management Staff":
        if mortFormQuery.is_posted == True :
            status = 'Approved'
        elif mortFormQuery.is_posted == False :
            status = 'Rejected'
        elif mortFormQuery.is_posted == None :
            status = 'Pending'

    elif request.user.groups.all()[0].name == "Extension Veterinarian":
        if mortFormQuery.is_reported == True and mortFormQuery.is_posted == True :
            status = 'Approved'
        elif mortFormQuery.is_reported == False and mortFormQuery.is_posted == True :
            status = 'Rejected'
        elif mortFormQuery.is_reported == None and mortFormQuery.is_posted == True :
            status = 'Pending'

    elif request.user.groups.all()[0].name == "Assistant Manager":
        if mortFormQuery.is_noted == True and mortFormQuery.is_reported == True and mortFormQuery.is_posted == True :
            status = 'Approved'
        elif mortFormQuery.is_noted == False and mortFormQuery.is_reported == True and mortFormQuery.is_posted == True :
            status = 'Rejected'
        elif mortFormQuery.is_noted == None and mortFormQuery.is_reported == True and mortFormQuery.is_posted == True : 
            status = 'Pending'
    
    elif request.user.groups.all()[0].name == "Field Technician":
        if mortFormQuery.is_noted == True and mortFormQuery.is_reported == True and mortFormQuery.is_posted == True :
            status = 'Approved'
        elif mortFormQuery.is_noted == False or mortFormQuery.is_reported == False or mortFormQuery.is_posted == False :
            status = 'Rejected'
        else :
            status = 'Pending'

    # get all mortalities under mortality form
    mortQuery = Mortality.objects.filter(mortality_form_id=mortalityFormID).all().order_by("id")
    mortList = []

    # store all data to an array
    for mortality in mortQuery:
        mortList.append({
            'id' : mortality.id,
            'mortality_date' : mortality.mortality_date,
            'format_date' : (mortality.mortality_date).strftime('%Y-%m-%d'),
            'num_begInv' : mortality.num_begInv,
            'num_today' : mortality.num_today,
            'num_toDate' : mortality.num_toDate,
            'source' : mortality.source,
            'remarks' : mortality.remarks,
        })

    # get all other versions of selected activity form
    versionList = Mortality_Form.objects.filter(series=mortFormQuery.series).all().order_by("-id")

    return render(request, 'healthtemp/selected-mortality-form.html', {'mortalityForm' : MortalityForm(), 'mortalities' : mortList, 'latest' : latestForm,
                                                                        'formStatus' : status, 'mortForm' : mortFormQuery, 'mortFormList' : versionList})

def approveMortalityForm(request, mortalityFormID):
    """
    - Modify is_posted, is_reported, and is_noted values of selected mortality form
    - Update last_updated and date_approved

    mortalityFormID = id value of mortality form selected
    """

    mortality_form = Mortality_Form.objects.filter(id=mortalityFormID).first()

    # get today's date
    dateToday = datetime.now(timezone.utc)

    if request.method == 'POST':
        print(request.POST)

        # update mortality form fields for user approvals
        # is_posted for paiwi mgt
        if request.POST.get("is_posted") == 'true' :
            mortality_form.is_posted = True

            if request.user.groups.all()[0].name == "Paiwi Management Staff":
                mortality_form.mort_mgtStaff_id = request.user.id

                # NOTIFY USER (EXTENSION VETERINARIAN) - A Mortality Form has been sent for approval or is pending for approval

                # NOTIFY USER (FIELD TECHNICIAN) - A Mortality Form has been approved by Paiwi Management Staff
    
        # is_reported for ext vet
        elif request.POST.get("is_reported") == 'true' :
            mortality_form.is_reported = True

            if request.user.groups.all()[0].name == "Extension Veterinarian":
                mortality_form.mort_extvet_id = request.user.id

                # NOTIFY USER (ASSISTANT MANAGER) - A Mortality Form has been sent for approval or is pending for approval

                # NOTIFY USER (FIELD TECHNICIAN) - A Mortality Form has been approved by Extension Veterinarian


        # is_noted for asst. manager
        elif request.POST.get("is_noted") == 'true' :
            mortality_form.is_noted = True

            if request.user.groups.all()[0].name == "Assistant Manager":
                mortality_form.mort_asm_id = request.user.id

                # NOTIFY USER (FIELD TECHNICIAN) - A Mortality Form has been approved by Assistant Manager

        
        mortality_form.save()

        # get all mortalities under mortality form
        mortQuery = Mortality.objects.filter(mortality_form_id=mortalityFormID).all()
        for mortality in mortQuery:
            mortality.last_updated = dateToday
            
            if mortality_form.is_noted == True and mortality_form.is_reported == True and mortality_form.is_posted == True :
                mortality.is_approved = True
                mortality.date_approved = dateToday

            mortality.save()
    

        messages.success(request, "Mortality Form has been approved by " + str(request.user.groups.all()[0].name) + ".", extra_tags='update-mortality')
        return JsonResponse({"success": "Mortality Form has been approved by " + str(request.user.groups.all()[0].name) + "."}, status=200)

    messages.error(request, "Failed to approve Mortality Form.", extra_tags='update-mortality')
    return JsonResponse({"error": "Not a POST method"}, status=400)

def rejectMortalityForm(request, mortalityFormID):
    """
    - Modify is_posted, is_reported, and is_noted values of selected mortality form
    - Update last_updated

    mortalityFormID = id value of mortality form selected
    """

    mortality_form = Mortality_Form.objects.filter(id=mortalityFormID).first()

    # get today's date
    dateToday = datetime.now(timezone.utc)

    if request.method == 'POST':
        print(request.POST)

        # update mortality form fields for user approvals
        # is_noted for asst. manager
        if request.POST.get("is_posted") == 'false' :
            mortality_form.is_posted = False

            if request.user.groups.all()[0].name == "Paiwi Management Staff":
                mortality_form.mort_mgtStaff_id = request.user.id
        
        # is_reported for ext vet
        elif request.POST.get("is_reported") == 'false' :
            mortality_form.is_reported = False

            if request.user.groups.all()[0].name == "Extension Veterinarian":
                mortality_form.mort_extvet_id = request.user.id

        # is_checked for live op
        elif request.POST.get("is_noted") == 'false' :
            mortality_form.is_noted = False

            if request.user.groups.all()[0].name == "Assistant Manager":
                mortality_form.mort_asm_id = request.user.id
        

        mortality_form.save()

        # duplicate instance (for a new version)
        mortality_form.pk = None
        mortality_form.save()

        # get all mortalities under mortality form
        mortQuery = Mortality.objects.filter(mortality_form_id=mortalityFormID).all()
        for mortality in mortQuery:
            mortality.last_updated = dateToday
            
            if mortality_form.is_noted == False or mortality_form.is_reported == False or mortality_form.is_posted == False :
                mortality.is_approved = False

            mortality.save()

            # duplicate instance (for a new version)
            mortality.pk = None
            mortality.mortality_form = mortality_form
            mortality.save()

        # NOTIFY USER (FIELD TECHNICIAN) - A Mortality Form has been rejected by <user>
        messages.success(request, "Mortality Form has been rejected by " + str(request.user.groups.all()[0].name) + ".", extra_tags='update-mortality')
        return JsonResponse({"success": "Mortality Form has been approved by " + str(request.user.groups.all()[0].name) + "."}, status=200)

    messages.error(request, "Failed to reject mortality records.", extra_tags='update-mortality')
    return JsonResponse({"error": "Not a POST method"}, status=400)

def resubmitMortalityForm(request, mortalityFormID, farmID, mortalityDate):
    """
    - Resubmit rejected mortality form and modify approval status
    - Add new mortality records to database and connect to mortality form (as FK)
    - Save details to mortality and add FK of current farm table
    """

    # get ID of current technician
    techID = request.user.id

    # get mortality form from ID
    mortality_form = Mortality_Form.objects.filter(id=mortalityFormID).first()

    # collected farmID of selected tech farm
    farmQuery = Farm.objects.get(pk=farmID)

    # get today's date
    dateToday = datetime.now(timezone.utc)

    if request.method == 'POST':
        # print(request.POST)
        numMortalities = int(len(request.POST)/4)

        # pass all values into each of the array mortalityList
        mortalityList = []

        i = 0
        while i < numMortalities:
            mort_date = str('mortalityList[') + str(i) + str('][mort_date]')
            today = str('mortalityList[') + str(i) + str('][today]')
            source = str('mortalityList[') + str(i) + str('][source]')
            remarks = str('mortalityList[') + str(i) + str('][remarks]')

            mortalityObject = {
                "mortDate" : request.POST.get(mort_date, default=None),
                "mortToday" : request.POST.get(today, default=None),
                "mortSource" : request.POST.get(source, default=None),
                "mortRemarks" : request.POST.get(remarks, default=None),
            }

            mortalityList.append(mortalityObject)
            i += 1
        
        # print("TEST LOG mortalityList: " + str(mortalityList))

        # reset approval status of mortality form
        mortality_form.is_posted = None
        mortality_form.is_reported = None
        mortality_form.is_noted = None
        mortality_form.date_added = datetime.now(timezone.utc)

        mortality_form.save()
        
        # pass all mortalityList objects into Mortality model
        x = 0

        for mort in mortalityList:
            mort = mortalityList[x]

            # create new instance of Mortality model for new records
            mortality = Mortality.objects.create(
                ref_farm_id = farmID,
                mortality_date = mort['mortDate'],
                num_begInv = farmQuery.total_pigs,
                num_today = mort['mortToday'],
                num_toDate = farmQuery.total_pigs - int(mort['num_today']),
                source = mort['mortSource'],
                remarks = mort['mortRemarks'],
                mortality_form_id = mortality_form.id
            )

            mortality.save()
            x += 1
        

        # NOTIFY USER (PAIWI MANAGEMENT STAFF) - A Mortality Form has been resubmitted by Field Technician; needs approval
        messages.success(request, "Mortality Form has been resubmitted.", extra_tags='update-mortality')
        return JsonResponse({"success": "Mortality Form has been resubmitted."}, status=200)

    messages.error(request, "Failed to resubmit Mortality Form.", extra_tags='update-mortality')
    return JsonResponse({"error": "Not a POST method"}, status=400)

def saveMortality(request, farmID, mortalityID):
    """
    - Update selected mortality record under current farm
    - Collect data from backend-scripts.js
    
    mortalityID - selected mortalityID passed as parameter
    farmID - selected farmID passed as parameter
    """
    # for setting Date input filters to today's date
    dateToday = datetime.now(timezone.utc)

    if request.method == 'POST':
        # print("TEST LOG: Edit Mortality is a POST Method")
        
        # collect data from inputs
        mortality_date = request.POST.get("mortality_date")
        num_begInv = request.POST.get("num_begInv")
        num_today = request.POST.get("num_today")
        num_toDate = request.POST.get("num_toDate")
        source = request.POST.get("source")
        remarks = request.POST.get("remarks")

        # get mortality to be updated
        mortality = Mortality.objects.filter(id=mortalityID).first()
        # print("OLD MORTALITY RECORD: " + str(mortality.mortality_date) + " - " + str(mortality.num_begInv) + " - " + str(mortality.num_today) + " to " + str(mortality.num_toDate) )

        # assign new values
        mortality.mortality_date = mortality_date
        mortality.num_begInv = num_begInv
        mortality.num_today = num_today
        mortality.num_toDate = num_toDate
        mortality.source = source
        mortality.remarks = remarks
        mortality.last_updated = dateToday
        
        mortality.save()
        # print("UPDATED MORTALITY RECORD: " + str(mortality.mortality_date) + " - " + str(mortality.num_begInv) + " - " + str(mortality.num_today) + " to " + str(mortality.num_toDate) )
        messages.success(request, "Mortality Record has been updated.", extra_tags='update-mortality')

        return JsonResponse({"success": "Mortality has been updated."}, status=200)

    return JsonResponse({"error": "Not a POST method"}, status=400)

def addWeight(request, farmID):
    """
    redirect to weight slip form or if method is POST, saves weight slip to database
    """
    
    try:
        Farm.objects.get(pk=farmID)
        # Farm.objects.get(pk=farmID)
    except:
        debug("farm does not exist")
        return redirect("healthSymptoms")

    if request.method == 'POST':
        # generate code number
        latestWeight = Farm_Weight.objects.last()
        try:
            code = int(latestWeight.code) + 1
        except:
            code = 1

        type = request.POST.get('weight-radio')

        # get latest Pigpen version
        latestPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()

        if type == 'starter':
            weight = Farm_Weight(
                date_filed = now(),
                ref_farm_id = farmID,
                is_starter = True,
                ave_weight = request.POST.get('ave_weight'),
                total_numHeads = request.POST.get('total_numHeads'),
                total_kls =  request.POST.get('total_kls'),
                remarks = request.POST.get('remarks'),
                code = code
            )
            weight.save()
            latestPigpen.start_weight = weight
        elif type == 'fattener':
            weight = Farm_Weight(
                date_filed = now(),
                ref_farm_id = farmID,
                is_starter = False,
                ave_weight = request.POST.get('ave_weight'),
                total_numHeads = request.POST.get('total_numHeads'),
                total_kls =  request.POST.get('total_kls'),
                remarks = request.POST.get('remarks'),
                code = code
            )
            weight.save()
            latestPigpen.final_weight =  weight

        latestPigpen.save()
        
    weightForm = WeightForm()
    return render(request, 'healthtemp/add-weight.html', {'weightForm': weightForm, 'farmID': int(farmID)})

def selectedWeightSlip(request, weightSlipID, weightDate):
    """
    - Display details of selected weight slip

    weightSlipID = id value of selected weight slip
    weightDate = date_filed value of selected weight slip
    """

    # get selected
    weightSlip = Farm_Weight.objects.filter(id=weightSlipID).first()

    # get latest
    latestSlip = Farm_Weight.objects.filter(code=weightSlip.code).last()

    # set status of mortality form
    if request.user.groups.all()[0].name == "Paiwi Management Staff":
        if weightSlip.is_posted == True :
            status = 'Approved'
        elif weightSlip.is_posted == False :
            status = 'Rejected'
        elif weightSlip.is_posted == None :
            status = 'Pending'

    elif request.user.groups.all()[0].name == "Assistant Manager":
        if weightSlip.is_noted  == True and weightSlip.is_posted == True :
            status = 'Approved'
        elif weightSlip.is_noted  == False and weightSlip.is_posted == True :
            status = 'Rejected'
        elif weightSlip.is_noted == None and weightSlip.is_posted == True : 
            status = 'Pending'
    
    elif request.user.groups.all()[0].name == "Field Technician":
        if weightSlip.is_noted == True and weightSlip.is_posted == True :
            status = 'Approved'
        elif weightSlip.is_noted == False or weightSlip.is_posted == False :
            status = 'Rejected'
        else :
            status = 'Pending'

    # get all other versions of selected weight slip
    versionList = Farm_Weight.objects.filter(code=weightSlip.code).all().order_by("-id")

    return render(request, 'healthtemp/selected-weight-slip.html', { 'weightForm' : Farm_Weight(), 'weight' : weightSlip, 'latest' : latestSlip,
                                                                    'formStatus' : status, 'weightList' : versionList })

def approveWeightSlip(request, weightSlipID):
    """
    - Modify is_posted, and is_noted values of selected weight slip
    """

    weight_slip = Farm_Weight.objects.filter(id=weightSlipID).first()

    if request.method == 'POST':
        print(request.POST)

        # update weight slip fields for user approvals
        # is_posted for paiwi mgt
        if request.POST.get("is_posted") == 'true' :
            weight_slip.is_posted = True

            if request.user.groups.all()[0].name == "Paiwi Management Staff":
                weight_slip.weight_mgtStaff_id = request.user.id

                # NOTIFY USER (ASSISTANT MANAGER) - A Weight Slip has been sent for approval or is pending for approval

                # NOTIFY USER (FIELD TECHNICIAN) - A Weight Slip has been approved by Paiwi Management Staff

        # is_noted for asst. manager
        elif request.POST.get("is_noted") == 'true' :
            weight_slip.is_noted = True

            if request.user.groups.all()[0].name == "Assistant Manager":
                weight_slip.weight_asm_id = request.user.id

                # NOTIFY USER (FIELD TECHNICIAN) - A Weight Slip has been approved by Assistant Manager

        
        weight_slip.save()    

        messages.success(request, "Weight Slip has been approved by " + str(request.user.groups.all()[0].name) + ".", extra_tags='update-weight')
        return JsonResponse({"success": "Weight Slip has been approved by " + str(request.user.groups.all()[0].name) + "."}, status=200)

    messages.error(request, "Failed to approve Weight Slip.", extra_tags='update-weight')
    return JsonResponse({"error": "Not a POST method"}, status=400)

def rejectWeightSlip(request, weightSlipID):
    """
    - Modify is_posted, and is_noted values of selected weight slip
    """

    weight_slip = Farm_Weight.objects.filter(id=weightSlipID).first()

    if request.method == 'POST':
        print(request.POST)

        # update weight slip fields for user approvals
        # is_posted for paiwi mgt
        if request.POST.get("is_posted") == 'false' :
            weight_slip.is_posted = False

            if request.user.groups.all()[0].name == "Paiwi Management Staff":
                weight_slip.weight_mgtStaff_id = request.user.id

                # NOTIFY USER (FIELD TECHNICIAN) - A Weight Slip has been rejected by Paiwi Management Staff

        # is_noted for asst. manager
        elif request.POST.get("is_noted") == 'false' :
            weight_slip.is_noted = False

            if request.user.groups.all()[0].name == "Assistant Manager":
                weight_slip.weight_asm_id = request.user.id

                # NOTIFY USER (FIELD TECHNICIAN) - A Weight Slip has been rejected by Assistant Manager

        
        weight_slip.save()

        # duplicate instance (for a new version)
        weight_slip.pk = None
        weight_slip.save()

        messages.success(request, "Weight Slip has been rejected by " + str(request.user.groups.all()[0].name) + ".", extra_tags='update-weight')
        return JsonResponse({"success": "Weight Slip has been rejected by " + str(request.user.groups.all()[0].name) + "."}, status=200)

    messages.error(request, "Failed to approve Weight Slip.", extra_tags='update-weight')
    return JsonResponse({"error": "Not a POST method"}, status=400)

# REPORTS for Module 2
def incidentsReported(request):
    debug("TEST LOG: in incidentRep /n")

    """
    Gets all Incident (Hog_Symptoms) records within existing dates and all Areas due to no selected filters in dropdown

    (1) date today
    (2) all Area records
    (3) Incident details
        - ID, Farm Code, Area, No. of Pigs Affected, Symptoms, Status, Date Reported
    """

    # for checking if filters were used in the displayed Report
    isFiltered = False

    # (1) for setting Date input filters to today's date
    dateToday = datetime.now(timezone.utc)

    # (2) all Area records
    areaQry = Area.objects.all()

    # (3.1) Incident details
    incidQry = Hog_Symptoms.objects.select_related('ref_farm').annotate(
        farm_code = F("ref_farm__id"),
        farm_area = F("ref_farm__area__area_name"),
        ).values(
            "id",
            "farm_code",
            "farm_area",
            "num_pigs_affected",
            "report_status",
            "date_filed"
            ).order_by("id")

    incidList = []
    total_pigs_affect = 0
    # total_symptoms = 0
    for f in incidQry:

        incidObject = {
            "id":                f["id"],
            "farm_code":         f["farm_code"],
            "farm_area":         f["farm_area"],
            "num_pigs_affected": f["num_pigs_affected"],
            "report_status":     f["report_status"],
            "date_filed":        f["date_filed"],
        }
        incidList.append(incidObject)

    # (3.2) Incidents Reported (symptoms list)
    symptomsList = Hog_Symptoms.objects.values(
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
    incident_symptomsList = zip(incidList, symptomsList)

    return render(request, 'healthtemp/rep-incidents-reported.html', {"isFiltered": isFiltered, 'dateStart': dateToday,'dateEnd': dateToday,
                                                                    "areaList": areaQry,
                                                                    "incident_symptomsList": incident_symptomsList})

def hogsMortality(request):
    debug("TEST LOG: in hogsMortality Report /n")

    """
    Gets all Mortality records within existing dates and all Areas due to no selected filters in dropdown

    (1) date today
    (2) all Area records
    (3) Mortality details
        - ID, Farm Code, Beg. Inventory, No. of Hogs Died, No. of Hogs To Date, Mortality Rate
    """

    # for checking if filters were used in the displayed Report
    isFiltered = False

    # (1) for setting Date input filters to today's date
    dateToday = datetime.now(timezone.utc)

    # (2) all Area records
    areaQry = Area.objects.all()

    # (3.1) Mortality details
    # latestPP = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()
    mortQry = Mortality.objects.filter(is_approved=True).order_by("id").all()
    # debug(str(mortQry.query))

    if not mortQry.exists(): # (ERROR) No Mortality records found.
        messages.error(request, "No Mortality records found.", extra_tags="mort-report")
        return render(request, 'healthtemp/rep-hogs-mortality.html', {"isFiltered": isFiltered,'areaList': areaQry,'dateStart': dateToday,'dateEnd': dateToday})


    mortality_rate = 0
    mRateList = [] 

    total_begInv = 0
    total_today = 0
    total_toDate = 0
    ave_mortRate = 0
    # (3.2) Mortality % per record, totals
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

        total_begInv += m.num_begInv
        total_today  += m.num_today
        total_toDate += m.num_toDate
        ave_mortRate += mortality_rate

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList)

    # compute ave of all mortality %
    if len(mortQry) > 0:
        ave_mortRate = round((ave_mortRate / len(mortQry)), 2)

    mortStats = {
        "total_begInv": total_begInv,
        "total_today":  total_today,
        "total_toDate": total_toDate,
        "ave_mortRate": ave_mortRate
    }

    return render(request, 'healthtemp/rep-hogs-mortality.html', {"isFiltered": isFiltered, 'dateStart': dateToday,'dateEnd': dateToday,
                                                                "areaList": areaQry, "mortList": mortalityList, "mortStats": mortStats})


def filter_mortalityRep(request, startDate, endDate, areaName):
    debug("TEST LOG: in filter_mortalityRep/n")

    """
    Gets Mortality records for each Farm based on (1) date range and (2) area name.

    (1) all Area records
    (2) Mortality details
        - ID, Farm Code, Beg. Inventory, No. of Hogs Died, No. of Hogs To Date, Mortality Rate
    """

    # debug("URL params:")
    # debug("startDate -- " + startDate)
    # debug("endDate -- " + endDate)
    # debug("areaName -- " + areaName)


    # convert str Dates to date type; then to a timezone-aware datetime
    sDate = make_aware(datetime.strptime(startDate, "%Y-%m-%d")) 
    eDate = make_aware(datetime.strptime(endDate, "%Y-%m-%d")) + timedelta(1) # add 1 day to endDate

    # debug("converted sDate -- " + str(type(sDate)))
    # debug("converted eDate -- " + str(type(eDate)))

    # for checking if filters were used in the displayed Report
    isFiltered = True

    # to revert endDate to same user date input
    truEndDate = eDate - timedelta(1)

    # (1) all Area records
    areaQry = Area.objects.all()

    if areaName == "All": # (CASE 1) search only by date range
        debug("TRACE: in areaName == 'All'")

        mortQry = Mortality.objects.filter(mortality_date__range=(sDate, eDate)).filter(is_approved=True).order_by("id").all()

        if not mortQry.exists(): # (ERROR) No Mortality records found.
            messages.error(request, "No Mortality records found.", extra_tags="mort-report")
            return render(request, 'healthtemp/rep-hogs-mortality.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})


    else: # (CASE 2) search by BOTH date range and areaName
        debug("TRACE: in else/")

        mortQry = Mortality.objects.filter(mortality_date__range=(sDate, eDate)).filter(ref_farm__area__area_name=areaName).filter(is_approved=True).order_by("id").all()

        if not mortQry.exists(): # (ERROR) No Mortality records found.
            messages.error(request, "No Mortality records found.", extra_tags="mort-report")
            return render(request, 'healthtemp/rep-hogs-mortality.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})


    mortality_rate = 0
    mRateList = [] 

    total_begInv = 0
    total_today = 0
    total_toDate = 0
    ave_mortRate = 0
    # (3.2) Mortality % per record, totals
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

        total_begInv += m.num_begInv
        total_today  += m.num_today
        total_toDate += m.num_toDate
        ave_mortRate += mortality_rate

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList)

    # compute ave of all mortality %
    if len(mortQry) > 0:
        ave_mortRate = round((ave_mortRate / len(mortQry)), 2)

    mortStats = {
        "total_begInv": total_begInv,
        "total_today":  total_today,
        "total_toDate": total_toDate,
        "ave_mortRate": ave_mortRate
    }

    return render(request, 'healthtemp/rep-hogs-mortality.html', {"areaName": areaName, "isFiltered": isFiltered, 'dateStart': sDate,'dateEnd': truEndDate,
                                                                "areaList": areaQry, "mortList": mortalityList, "mortStats": mortStats})



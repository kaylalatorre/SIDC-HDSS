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
    Pigpen_Group, Pigpen_Row, Hog_Weight, 
    Disease_Case, Disease_Record)

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

# for Forms
from farmsapp.forms import (
    MortalityForm,
    WeightForm
)

# import regex
import re

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

        # collect pigpens
        latestPP = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()
        pigpenQry = Pigpen_Row.objects.filter(pigpen_grp_id=latestPP.id).order_by("id")
        
        total_pigs = 0
        for pen in pigpenQry:
            total_pigs += pen.num_heads

        # Get latest Mortality record of the Farm (w Pigpen filter)
        # mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=latestPP.id).values("num_toDate").order_by('-mortality_date').first()
        mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=latestPP.id).values("num_toDate").last()

        mortality_rate = 0

        if mortQry is not None:
            mortality_rate = (mortQry.get("num_toDate") / total_pigs) * 100
    
    # compute mortality % with the given mortalityID
    if mortalityID is not None:
        mortObj = Mortality.objects.filter(id=mortalityID).first()

        if mortObj is not None:
            mortality_rate = (mortObj.num_toDate / mortObj.num_begInv) * 100

    return round(mortality_rate, 2)


def categHogWeight(weight_list):

    ctr_base = 0
    ctr_low = 0
    ctr_med = 0
    ctr_high = 0
    ctr_ceil = 0
    ctr_marketable = 0

    for w in weight_list:
        # classify given hog weight
        if w.final_weight in range(0, 60):
            ctr_base += 1
        elif w.final_weight in range(60, 81):
            ctr_low += 1
        elif w.final_weight in range(80, 101):
            ctr_med += 1
        elif w.final_weight in range(100, 121):
            ctr_high += 1
        elif w.final_weight > 120:
            ctr_ceil += 1

    ctr_marketable = ctr_high + ctr_ceil

    return ctr_base, ctr_low, ctr_med, ctr_high, ctr_ceil, ctr_marketable


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
        mem_code=F("hog_raiser__mem_code"), 
        farm_area = F("area__area_name"),
        ).values(
            "id",
            "fname",
            "lname", 
            "mem_code",
            "farm_area",
            "total_pigs",
            "last_updated",
            ).order_by("id")
    # debug(qry)


    if not qry.exists(): 
        return render(request, 'healthtemp/hogs-health.html', {"areaList": areaQry})
    else:

        farmsData = []
        total_pigs = 0
        total_incidents = 0
        total_active = 0

        for f in qry:
            start_weight = 0.0
            end_weight   = 0.0
            end_subtotal = 0.0
            pigs_sold = 0

            farmID = f["id"]

            # get latest version of Pigpen
            latestPP = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()

            # get current starter and fattener weights acc. to current Pigpen
            s_weightQry = Farm_Weight.objects.filter(pigpen_grp_id=latestPP.id).filter(is_starter=True).first()
            e_weightQry = Farm_Weight.objects.filter(pigpen_grp_id=latestPP.id).filter(is_starter=False).all()

            # error checking for None weight values per Farm
            if s_weightQry is not None:
                start_weight = s_weightQry.ave_weight

            if len(e_weightQry):
                for e in e_weightQry:
                    end_subtotal += e.total_kls
                    pigs_sold += e.total_numHeads

                end_weight = end_subtotal/pigs_sold

            # for computing Mortality %
            mortality_rate = compute_MortRate(farmID, None)

            # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
            total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPP.id).count()

            # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
            total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPP.id).filter(report_status="Active").count()

            farmObject = {
                "code":             f["id"],
                "raiser":           " ".join((f["fname"],f["lname"])),
                "r_mem_code":       f["mem_code"],
                "area":             f["farm_area"],
                "pigs":             f["total_pigs"],
                "updated":          f["last_updated"],
                "ave_startWeight":  start_weight,
                "ave_endWeight":    round(end_weight, 2),
                "mortality_rate":   mortality_rate,
                "total_incidents":  total_incidents,
                "total_active":     total_active,
            }
            farmsData.append(farmObject)

            total_pigs += f["total_pigs"]
        # debug(farmsData)

        sorted_farmList = sorted(farmsData, key = lambda i: i['total_active'], reverse=True)


        return render(request, 'healthtemp/hogs-health.html', {"areaList": areaQry, "farmList": sorted_farmList})


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
        mem_code=F("hog_raiser__mem_code"), 
        farm_area = F("area__area_name"),
        ).values(
            "id",
            "fname",
            "lname", 
            "mem_code",
            "farm_area",
            "total_pigs",
            "last_updated",
            ).first()
    # debug(qry)

    if selectFarm is None: 
        return render(request, 'healthtemp/selected-hogs-health.html', {})

    # get current starter and fattener weights acc. to current Pigpen
    latestPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()
    
    start_weight = Farm_Weight.objects.filter(is_starter=True).filter(pigpen_grp_id=latestPigpen.id).first()
    final_weight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=latestPigpen.id).all()
    
    # collated data for fattener weight slips
    total_kls = 0.0
    total_numHeads = 0
    if len(final_weight) > 0:
        for f in final_weight:
            date_filed = f.date_filed
            total_kls += f.total_kls
            total_numHeads += f.total_numHeads
            remarks = f.remarks

        end_weight = {
            'date_filed' : date_filed,
            'ave_weight' : round((total_kls/total_numHeads), 2),
            'total_numHeads' : total_numHeads,
            'total_kls' : round(total_kls, 2),
            'remarks' : remarks
        }
        # print(end_weight)
    
    else: 
        end_weight = { }

    # get final weight slip
    final_weight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=latestPigpen.id).last()

    # collecting all past pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()
    lastPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()

    versionList = []
    for pen in allPigpens:
        fWeight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=pen.id).last()
        # debug(fWeight.date_filed)

        if latestPigpen.id == pen.id and int(selectFarm.get('total_pigs')) == 0:
                verObj = { 'date_added' : pen.date_added,
                            'endDate' : fWeight.date_filed,
                            'id' : pen.id }
        else:
            if fWeight is not None:
                verObj = {
                    'date_added' : pen.date_added,
                    'endDate' : fWeight.date_filed,
                    'id' : pen.id }
            else: 
                verObj = {
                    'date_added' : pen.date_added,
                    'endDate' : None,
                    'id' : pen.id }
        
        versionList.append(verObj)


    total_incidents = 0
    total_active = 0

    # for computing Mortality %
    mortality_rate = compute_MortRate(farmID, None)

    # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
    total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPigpen.id).count()

    # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
    total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(report_status="Active").filter(pigpen_grp_id=latestPigpen.id).count()

    farmObject = {
        "code":  int(farmID),
        "raiser": " ".join((selectFarm["fname"], selectFarm["lname"])),
        "r_mem_code": selectFarm["mem_code"],
        "area": selectFarm["farm_area"],
        "pigs": selectFarm["total_pigs"],
        "updated": selectFarm["last_updated"],

        "start_weight": start_weight,
        "end_weight": end_weight,

        "mortality_rate": mortality_rate,
        "total_incidents": total_incidents,
        "total_active": total_active,
    }


    # (2.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPigpen.id).only(
        'date_filed', 
        'report_status',
        'num_pigs_affected').order_by("-date_filed").all()

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
            'conjunctivitis').order_by("-date_filed").all()

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidentQry, symptomsList)

    # (3.1) Mortality Records
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=latestPigpen.id).select_related(
                    'mortality_form').annotate(series=F("mortality_form__series")).order_by("-id").all()

    mortality_rate = 0
    mRateList = []
    mCaseList = [] 
    # (3.2) Mortality % per record
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

        mCaseList.append(m.case_no)

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList, mCaseList)

    # for getting length of Incident records
    total_incidents = incidentQry.count()
    total_mortalities = mortQry.count()

    # (4) hog weight count acc. to weight range, no. of pigs reached market weight (100kg <)
    f_weightQry = Hog_Weight.objects.filter(farm_weight__ref_farm = farmID).all()

    weightList = categHogWeight(f_weightQry)

    return render(request, 'healthtemp/selected-hogs-health.html', {"total_incidents": total_incidents, "total_mortalities": total_mortalities, "farm": farmObject, "incident_symptomsList": incident_symptomsList,
                                                                    "mortalityList": mortalityList, 'version' : versionList, 'selectedPigpen' : latestPigpen, 'latest' : latestPigpen, "weightList": weightList, "fattener": final_weight})

def selectedHogsHealthVersion(request, farmID, farmVersion):
    """
    Displays information of selected hogs health record for assistant manager

    :param farmID: PK of selected farm
    :type farmID: string

    :param farmVersion: id of farm version (pigpen group)
    :type farmVersion: string
    """

    # TODO: remove select_related on farm_weight here
    # (1) get farm based on farmID; get related data from hog_raiser, area, farm_weight
    selectFarm = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'farm_weight').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        mem_code=F("hog_raiser__mem_code"), 
        farm_area = F("area__area_name"),
        ).values(
            "id",
            "fname",
            "lname", 
            "mem_code",
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
    selectedPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).filter(id=farmVersion).first()
    lastPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()

    # get final weight slip
    fattener = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=selectedPigpen.id).last()

    versionList = []
    for pen in allPigpens:
        fWeight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=pen.id).last()
        # debug(fWeight.date_filed)

        if selectedPigpen.id == pen.id and int(selectFarm.get('total_pigs')) == 0:
                verObj = { 'date_added' : pen.date_added,
                            'endDate' : fWeight.date_filed,
                            'id' : pen.id }
        else:
            if fWeight is not None:
                verObj = {
                    'date_added' : pen.date_added,
                    'endDate' : fWeight.date_filed,
                    'id' : pen.id }
            else: 
                verObj = {
                    'date_added' : pen.date_added,
                    'endDate' : None,
                    'id' : pen.id }
        
        versionList.append(verObj)

    # get current starter and fattener weights acc. to current Pigpen
    start_weight = Farm_Weight.objects.filter(is_starter=True).filter(pigpen_grp_id=selectedPigpen.id).first()
    final_weight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=selectedPigpen.id).all()
    
    # collated data for fattener weight slips
    total_kls = 0.0
    total_numHeads = 0
    if len(final_weight) > 0:
        for f in final_weight:
            date_filed = f.date_filed
            total_kls += f.total_kls
            total_numHeads += f.total_numHeads
            remarks = f.remarks

        end_weight = {
            'date_filed' : date_filed,
            'ave_weight' : round((total_kls/total_numHeads), 2),
            'total_numHeads' : total_numHeads,
            'total_kls' : round(total_kls, 2),
            'remarks' : remarks
        }
        # print(end_weight)
    
    else: 
        end_weight = { }

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
        "r_mem_code": selectFarm["mem_code"],
        "area": selectFarm["farm_area"],
        "pigs": selectFarm["total_pigs"],
        "updated": selectFarm["last_updated"],
        
        "start_weight": start_weight,
        "end_weight": end_weight,

        "mortality_rate": mortality_rate,
        "total_incidents": total_incidents,
        "total_active": total_active,
    }


    # (2.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=selectedPigpen.id).only(
        'date_filed', 
        'report_status',
        'num_pigs_affected').order_by("-date_filed").all()

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
            'conjunctivitis').order_by("-date_filed").all()

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidentQry, symptomsList)

    # (3.1) Mortality Records
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=selectedPigpen.id).select_related(
                    'mortality_form').annotate(series=F("mortality_form__series")).order_by("-id").all()

    mortality_rate = 0
    mRateList = [] 
    mCaseList = [] 
    # (3.2) Mortality % per record
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

        mCaseList.append(m.case_no)

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList, mCaseList)

    # for getting length of Incident, Mortality records
    total_incidents = incidentQry.count()
    total_mortalities = mortQry.count()
    # debug("total_incidents -- " + str(total_incidents))

    # (4) hog weight count acc. to weight range, no. of pigs reached market weight (100kg <)
    f_weightQry = Hog_Weight.objects.filter(farm_weight__ref_farm = farmID).all()

    weightList = categHogWeight(f_weightQry)

    return render(request, 'healthtemp/selected-hogs-health.html', {"total_incidents": total_incidents, "total_mortalities": total_mortalities, "farm": farmObject, "incident_symptomsList": incident_symptomsList,
                                                                    "mortalityList": mortalityList, 'version' : versionList, 'selectedPigpen' : selectedPigpen, 'latest' : lastPigpen, "weightList": weightList, "fattener": fattener})


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
        qry = Farm.objects.filter(area_id=area.id).select_related('hog_raiser').annotate(
            fname=F("hog_raiser__fname"), 
            lname=F("hog_raiser__lname"), 
            mem_code=F("hog_raiser__mem_code"), 
            ).values(
                "id",
                "fname",
                "lname", 
                "mem_code",
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
            end_subtotal = 0.0
            pigs_sold = 0

            farmID = f["id"]
            
            # get latest version of Pigpen
            latestPP = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()

            # get current starter and fattener weights acc. to current Pigpen
            s_weightQry = Farm_Weight.objects.filter(is_starter=True).filter(pigpen_grp_id=latestPP.id).first()
            e_weightQry = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=latestPP.id).all()
            # print(e_weightQry)

            # error checking for None weight values per Farm
            if s_weightQry is not None:
                start_weight = s_weightQry.ave_weight
                # print("farm " + str(f["id"]) + " " + str(start_weight))

            if len(e_weightQry):
                for e in e_weightQry:
                    end_subtotal += e.total_kls
                    pigs_sold += e.total_numHeads

                end_weight = end_subtotal/pigs_sold


            # for computing Mortality %
            mortality_rate = compute_MortRate(farmID, None)
        
            # for "Incidents Reported" column --> counts how many Symptoms record FK-ed to a Farm
            total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPP.id).count()

            # for "Active Incidents" column --> counts how many Symptoms record with "Active" status
            total_active = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPP.id).filter(report_status="Active").count()

            farmObject = {
                "area":             area.area_name,
                "code":             f["id"],
                "raiser":           " ".join((f["fname"],f["lname"])),
                "r_mem_code":       f["mem_code"],
                "pigs":             f["total_pigs"],
                "updated":          f["last_updated"],
                "ave_startWeight":  start_weight,
                "ave_endWeight":    round(end_weight, 2),
                "mortality_rate":   mortality_rate,
                "total_incidents":  total_incidents,
                "total_active":     total_active,
            }
            farmsData.append(farmObject)

            total_pigs += f["total_pigs"]
        # debug("-- farmsData ---")
        # debug(farmsData)

        sorted_farmList = sorted(farmsData, key = lambda i: i['total_active'], reverse=True)


    # (ERROR) for checking technician Areas that have no assigned Farms
    if not farmsData: 
        # messages.error(request, "Hogs health record/s not found.", extra_tags="view-healthSymp")
        return render(request, 'healthtemp/health-symptoms.html', {})


    return render(request, 'healthtemp/health-symptoms.html', {"farmList": sorted_farmList})

def selectedHealthSymptoms(request, farmID):
    """
    Displays information of selected hogs health record for Technician user.

    :param farmID: PK of selected farm
    :type farmID: string
    """
    
    # get current total_pigs
    farm = Farm.objects.filter(id=farmID).values("total_pigs").first()

    # get current starter and fattener weights acc. to current Pigpen
    latestPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()

    start_weight = Farm_Weight.objects.filter(is_starter=True).filter(pigpen_grp_id=latestPigpen.id).first()
    final_weight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=latestPigpen.id).all()
    
    # collated data for fattener weight slips
    total_kls = 0.0
    total_numHeads = 0
    if len(final_weight) > 0:
        for f in final_weight:
            date_filed = f.date_filed
            total_kls += f.total_kls
            total_numHeads += f.total_numHeads
            remarks = f.remarks

        end_weight = {
            'date_filed' : date_filed,
            'ave_weight' : round((total_kls/total_numHeads), 2),
            'total_numHeads' : total_numHeads,
            'total_kls' : round(total_kls, 2),
            'remarks' : remarks
        }
        # print(end_weight)
    
    else: 
        end_weight = { }

    # collecting all past pigpens (versions)
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()
    lastPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()

    # get final weight slip
    fattener = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=latestPigpen.id).last()

    versionList = []
    for pen in allPigpens:
        fWeight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=pen.id).last()
        # debug(fWeight.date_filed)

        if latestPigpen.id == pen.id and int(farm.get('total_pigs')) == 0:
                verObj = { 'date_added' : pen.date_added,
                            'endDate' : fWeight.date_filed,
                            'id' : pen.id }
        else:
            if fWeight is not None:
                verObj = {
                    'date_added' : pen.date_added,
                    'endDate' : fWeight.date_filed,
                    'id' : pen.id }
            else: 
                verObj = {
                    'date_added' : pen.date_added,
                    'endDate' : None,
                    'id' : pen.id }
        
        versionList.append(verObj)

    # (1.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=latestPigpen.id).only(
        'date_filed',
        'date_updated', 
        'report_status',
        'num_pigs_affected').order_by("-date_filed").all()

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
            'conjunctivitis').order_by("-date_filed").all()
    

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidentQry, symptomsList, editList)

    # (2) Mortality Records
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=latestPigpen.id).select_related(
                    'mortality_form').annotate(series=F("mortality_form__series")).order_by("-id").all()

    mortality_rate = 0
    mRateList = [] 
    mCaseList = [] 
    # (3.2) Mortality % per record
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

        mCaseList.append(m.case_no)

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList, mCaseList)

    # for getting length of Incident records
    total_incidents = incidentQry.count()
    total_mortalities = mortQry.count()

    # (4) hog weight count acc. to weight range, no. of pigs reached market weight (100kg <)
    f_weightQry = Hog_Weight.objects.filter(farm_weight__ref_farm = farmID).all()

    weightList = categHogWeight(f_weightQry)


    # (5) Confirmed Cases table data
    casesQry = Disease_Record.objects.filter(ref_disease_case__incid_case__pigpen_grp=latestPigpen.id).filter(ref_disease_case__incid_case__ref_farm=farmID).select_related('ref_disease_case').annotate(
        case_code        = F("ref_disease_case__id"),
        lab_ref_no       = F("ref_disease_case__lab_ref_no"),
        incid_no         = F("ref_disease_case__incid_case"),
        num_pigs_affect  = F("ref_disease_case__num_pigs_affect"),
        disease_name     = F("ref_disease_case__disease_name"),
        date_updated     = F("ref_disease_case__date_updated"),
    ).order_by("-date_filed", "lab_ref_no").values()
    # debug(casesQry)

    cases = []
    if casesQry.exists():

        casesList = []
        for case in casesQry:
            if case['lab_ref_no'] not in casesList:
                casesList.append(case['lab_ref_no'])

                if case['total_recovered'] is not None and case['total_died'] is not None:
                    case['max_recovered'] = int(case['num_pigs_affect']) - (int(case['total_recovered']) + int(case['total_died']))
                else:
                    case['max_recovered'] = 0

                cases.append(case)
                # debug(casesList)
                # debug("case['max_recovered']: " + str(case['max_recovered']))
    # debug(cases)

    return render(request, 'healthtemp/selected-health-symptoms.html', {"total_incidents": total_incidents, "total_mortalities": total_mortalities, "farm_code": int(farmID), 'latest' : latestPigpen,
                                                                        "incident_symptomsList": incident_symptomsList, "mortalityList": mortalityList, 'version' : versionList,
                                                                        'selectedPigpen' : latestPigpen, "start_weight": start_weight, "end_weight": end_weight,
                                                                        "weightList": weightList, 'total_pigs': farm.get("total_pigs"), 'total_disease' : len(cases), 'dTable': cases })


def selectedHealthSymptomsVersion(request, farmID, farmVersion):
    """
    Displays information of selected hogs health record for Technician user.

    :param farmID: PK of selected farm
    :type farmID: string
    
    :param farmVersion: id of farm version (pigpen group)
    :type farmVersion: string
    """

    # get current total_pigs
    farm = Farm.objects.filter(id=farmID).values("total_pigs").first()

   # collecting all past pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()
    selectedPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).filter(id=farmVersion).first()
    lastPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()

    # get final weight slip
    fattener = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=selectedPigpen.id).last()

    versionList = []
    for pen in allPigpens:
        fWeight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=pen.id).last()
        # debug(fWeight.date_filed)

        if selectedPigpen.id == pen.id and int(farm.get('total_pigs')) == 0:
                verObj = { 'date_added' : pen.date_added,
                            'endDate' : fWeight.date_filed,
                            'id' : pen.id }
        else:
            if fWeight is not None:
                verObj = {
                    'date_added' : pen.date_added,
                    'endDate' : fWeight.date_filed,
                    'id' : pen.id }
            else: 
                verObj = {
                    'date_added' : pen.date_added,
                    'endDate' : None,
                    'id' : pen.id }
        
        versionList.append(verObj)

    # get current starter and fattener weights acc. to current Pigpen
    start_weight = Farm_Weight.objects.filter(is_starter=True).filter(pigpen_grp_id=selectedPigpen.id).first()
    final_weight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=selectedPigpen.id).all()
    
    # collated data for fattener weight slips
    total_kls = 0.0
    total_numHeads = 0
    if len(final_weight) > 0:
        for f in final_weight:
            date_filed = f.date_filed
            total_kls += f.total_kls
            total_numHeads += f.total_numHeads
            remarks = f.remarks

        end_weight = {
            'date_filed' : date_filed,
            'ave_weight' : round((total_kls/total_numHeads), 2),
            'total_numHeads' : total_numHeads,
            'total_kls' : round(total_kls, 2),
            'remarks' : remarks
        }
        # print(end_weight)
    
    else: 
        end_weight = { }

    # (1.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
    incidentQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).filter(pigpen_grp_id=selectedPigpen.id).only(
        'date_filed',
        'date_updated', 
        'report_status',
        'num_pigs_affected').order_by("-date_filed").all()

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
            'conjunctivitis').order_by("-date_filed").all()
    

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidentQry, symptomsList, editList)

    # (2) Mortality Records
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=selectedPigpen.id).select_related(
                    'mortality_form').annotate(series=F("mortality_form__series")).order_by("-id").all()

    mortality_rate = 0
    mRateList = [] 
    mCaseList = [] 
    # (3.2) Mortality % per record
    for m in mortQry:
        mortality_rate = compute_MortRate(None, m.id)
        mRateList.append(mortality_rate)

        mCaseList.append(m.case_no)

    # temporarily combine mortality qry w/ computed mortality % in one list
    mortalityList = zip(mortQry, mRateList, mCaseList)

    # for getting length of Incident, Mortality records
    total_incidents = incidentQry.count()
    total_mortalities = mortQry.count()

    # (4) hog weight count acc. to weight range, no. of pigs reached market weight (100kg <)
    f_weightQry = Hog_Weight.objects.filter(farm_weight__ref_farm = farmID).all()

    weightList = categHogWeight(f_weightQry)

    # (5) Confirmed Cases table data
    casesQry = Disease_Record.objects.filter(ref_disease_case__incid_case__pigpen_grp=selectedPigpen.id).filter(ref_disease_case__incid_case__ref_farm=farmID).annotate(
        case_code        = F("ref_disease_case__id"),
        lab_ref_no       = F("ref_disease_case__lab_ref_no"),
        incid_no         = F("ref_disease_case__incid_case"),
        num_pigs_affect  = F("ref_disease_case__num_pigs_affect"),
        disease_name     = F("ref_disease_case__disease_name"),
        date_updated     = F("ref_disease_case__date_updated"),
    ).order_by("-date_filed", "lab_ref_no").values()
    # debug(casesQry)

    cases = []
    if casesQry.exists():

        casesList = []
        for case in casesQry:
            if case['lab_ref_no'] not in casesList:
                casesList.append(case['lab_ref_no'])

                if case['total_recovered'] is not None and case['total_died'] is not None:
                    case['max_recovered'] = int(case['num_pigs_affect']) - (int(case['total_recovered']) + int(case['total_died']))
                else:
                    case['max_recovered'] = 0
                    
                cases.append(case)
    # debug(cases)

    return render(request, 'healthtemp/selected-health-symptoms.html', {"total_incidents": total_incidents, "total_mortalities": total_mortalities, "farm_code": int(farmID), 'latest' : lastPigpen,
                                                                        "incident_symptomsList": incident_symptomsList, "mortalityList": mortalityList, 'version' : versionList,
                                                                        'selectedPigpen' : selectedPigpen, "start_weight": start_weight, "end_weight": end_weight, 'fattener' : fattener,
                                                                        "weightList": weightList, 'total_pigs': int(0), 'total_disease' : len(cases), 'dTable': cases })


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
        # debug("select_status -- " + select_status)

        remarks = request.POST.get("remarks")
        # debug("remarks -- " + remarks)

        # search if Incident exists in db
        incidentObj = Hog_Symptoms.objects.filter(id=incidID).first()

        # get date diff of date_filed from date_updated
        repDateDiff = datetime.now(timezone.utc) - incidentObj.date_updated
        # debug("repDateDiff.days -- " + str(repDateDiff.days))

        if incidentObj is not None:
            # (ERROR 1) if select_status is ACTIVE & db_status is PENDING 
            if select_status == "Active" and incidentObj.report_status == "Pending":
                return JsonResponse({"error": "Cannot set [PENDING] report status back to [ACTIVE].", "status_code":"400"}, status=400)

            # (ERROR 2) if db_status is RESOLVED & exceeds 1 day
            # Note: already handled in selectedHealthSymptoms()

            else: # (SUCCESS) No restrictions, can edit report_status
                incidentObj.report_status = select_status
                incidentObj.remarks = remarks
                incidentObj.save()

                debug("(SUCCESS) Incident status successfully updated.")

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
        
        farm = Farm.objects.filter(id=farmID).first()

        # get farmID from URL param and check if Farm record exists
        if Farm.objects.filter(id=farmID).exists():

            # debug("in POST addCase /n: farmID -- " + str(farmID))
            
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
            if len(symptomsArr) > 0 and int(num_pigsAffected) > 0 and symptomsArr.count(False) < 22: # (SUCCESS) Symptoms list is complete, proceed to add in db
                
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
                    df = ts.strftime("%m/%d/%Y")
                    # debug(incidObj.date_filed)
                    
                    # debug("[death] 11 value -- " + str(symptomsArr[11]) + "// [death] 12 value -- " + str(symptomsArr[12]))

                    # debug("(SUCCESS) Incident report added.")

                    # update last_updated of farm
                    farm.last_updated = datetime.now(timezone.utc)
                    farm.save()

                    # (SUCCESS) Incident has been added. Properly redirect to selected view page
                    # IF death is in the symptoms
                    if symptomsArr[11] == True or symptomsArr[12] == True:
                        messages.success(request, "New incident report has been successfully added. Death is one of the symptoms reported.", extra_tags='add-incidCase-death' + str(farmID))
                    # else
                    else:
                        messages.success(request, "New incident report dated " + df + " has been successfully added.", extra_tags='add-incidCase')
                    
                    return JsonResponse({"status_code":"200"}, status=200)
        
                else: # (ERROR) User input of num_pigs is not w/in total_pigs range
                    debug("ERROR: Input only no. of pigs within total hogs of Farm.")
                    messages.error(request, "Input only no. of pigs within total hogs of Farm.", extra_tags='add-incidCase')
                    return JsonResponse({"error": "Input only no. of pigs within total hogs of Farm.", "status_code":"400"}, status=400)
            
            else: # (ERROR) No checked symptoms for Incident Case, no. pigs affected is 0
                debug("ERROR: Incomplete input/s for Incident Case.")
                messages.error(request, "Incomplete input/s for Incident Case.", extra_tags='add-incidCase')
                return JsonResponse({"error": "Incomplete input/s for Incident Case.", "status_code":"400"}, status=400)
        
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
    latestForm = Mortality_Form.objects.order_by("-series").first()
    try:
        series = int(latestForm.series) + 1
    except:
        series = 1

    # collected farmID of selected tech farm
    farmQuery = Farm.objects.get(pk=farmID)

    # get current Farm version
    farmVersion = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()

    # get all active and pending incident cases for the farm
    incidQry = Hog_Symptoms.objects.filter(ref_farm_id=farmID).order_by('-id')
    # debug(incidQry)
    
    # get all disease cases for the farm
    disCases = []
    for incid in incidQry:
        disQry = Disease_Case.objects.filter(incid_case_id=incid.id).filter(end_date=None).values("id", "start_date").order_by('-id')

        if disQry:
            for dis in disQry:
                disCases.append([dis['start_date'], dis['id']])
        else:
            disCases.append(None)
    
    # debug(disCases)

    # get last mortality record
    mortQry = Mortality.objects.filter(ref_farm_id=farmID).filter(mortality_form__pigpen_grp_id=farmVersion.id).values("num_toDate").last()

    # get beginning inventory value
    pigpenQry = Pigpen_Row.objects.filter(pigpen_grp_id=farmVersion.id).all()
    
    num_begInv = 0
    for pen in pigpenQry:            
        num_begInv += pen.num_heads

    # get toDate value
    latest_toDate = 0
    if mortQry :
        latest_toDate = int(mortQry.get("num_toDate"))

    if request.method == 'POST':
        # print("TEST LOG: Add Mortality has POST method") 
        # print(request.POST)

        mortalityForm = MortalityForm(request.POST)

        # pass all values into one record in mortalityList
        mortalityList = []
        
        i = 0
        for mortality_date in request.POST.getlist('mortality_date', default=None):
            sourceOptions = str("sourceOptions-")+str(i)
            # print(sourceOptions)

            if request.POST.getlist('case', default=None)[i] == '- - -':
                case_no = None
            else:
                case_no = request.POST.getlist('case', default=None)[i]

            mortalityObject = {
                "mortality_date" : request.POST.getlist('mortality_date', default=None)[i],
                "num_today" : request.POST.getlist('num_today', default=None)[i],
                "source" : request.POST.getlist(sourceOptions, default=None)[0],
                "case" : case_no,
                "remarks" : request.POST.getlist('remarks', default=None)[i],
            }
            
            mortalityList.append(mortalityObject)
            i += 1

        if mortalityForm.is_valid():
            
            # create instance of Mortality Form model
            mortality_form = Mortality_Form.objects.create(
                series = series,
                date_added = datetime.now(timezone.utc),
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
                    num_begInv = num_begInv,
                    num_today = mort['num_today'],
                    num_toDate = latest_toDate + int(mort['num_today']),
                    source = mort['source'],
                    case_no = mort['case'],
                    remarks = mort['remarks'],
                    mortality_form_id = mortality_form.id
                )

                farmQuery.total_pigs -= int(mort['num_today'])
            
                # print(str(mortality))
                mortality.save()
                x += 1
                latest_toDate += int(mort['num_today'])

                # update or create disease record (if source == disease)
                if mort['source'] == "Disease Case":
                    
                    # get latest disease record of selected disease case
                    latestDR = Disease_Record.objects.filter(ref_disease_case=mort['case']).order_by("-date_filed").first()
                    updateDC = Disease_Case.objects.filter(id=mort['case']).first()

                    print(latestDR.date_filed)
                    print(mort['mortality_date'])
                    
                    if (str(latestDR.date_filed) == str(mort['mortality_date'])):
                        # print("update record")
                        latestDR.num_died = (int(mort['num_today']) + latestDR.num_died)
                        latestDR.total_died = (int(mort['num_today']) + latestDR.total_died)
                        latestDR.save()

                        # update "date_updated" of Disease Case to date-time today
                        updateDC.date_updated =  datetime.now(timezone.utc)
                        updateDC.save()

                    else: # make new Disease Record for the Case if none exists today
                        # print("new record")
                        newDR = Disease_Record()
                        newDR.date_filed = datetime.strptime(str(mort['mortality_date']), '%Y-%m-%d')
                        newDR.num_recovered = 0
                        newDR.num_died = int(mort['num_today'])

                        # add created record to totals
                        newDR.total_recovered = latestDR.total_recovered
                        newDR.total_died = (int(mort['num_today']) + latestDR.total_died)

                        # Qry disease case then FK whole object to disease record
                        newDR.ref_disease_case = updateDC

                        # update "date_updated" of Disease Case to date today
                        updateDC.date_updated =  datetime.now(timezone.utc)
                        updateDC.save()

                        # save new Disease record
                        newDR.save()

            # update last_updated of farm
            farmQuery.last_updated = datetime.now(timezone.utc)
            farmQuery.save()

            # NOTIFY USER (PAIWI MANAGEMENT STAFF) - New Mortality Record has been submitted by Field Technician OR New Mortality Record needs approval
            messages.success(request, "Mortality record has been successfully added.", extra_tags='add-mortality')
            return redirect('/selected-health-symptoms/' + str(farmID))

        else:
            # print("TEST LOG: mortalityForm is not valid")
            formError = str(mortalityForm.non_field_errors().as_text)

            messages.error(request, "Error adding mortality record. " + str(re.split("\'.*?",formError)[1]), extra_tags='add-mortality')

    else:
        print("TEST LOG: Add Mortality is not a POST method")

        mortalityForm = MortalityForm()
    
    return render(request, 'healthtemp/add-mortality.html', { 'farmID' : farmID, 'series' : series, 'mortalityForm' : mortalityForm, 'dis_cases' : disCases,
                                                                'num_begInv' : num_begInv, 'incid_cases' : incidQry, 'latest_toDate' : latest_toDate})


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
    
    # get total num. of pigs in farm
    farm = Farm.objects.filter(id=farmID).only("total_pigs").first()

    latestPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-date_added").first()
    start_weight = Farm_Weight.objects.filter(is_starter=True).filter(pigpen_grp_id=latestPigpen.id).first()

    weightType = ""
    if start_weight == None:
        weightType = 'starter'
    else:
        weightType = "fattener"

    if request.method == 'POST':

        if start_weight == None:
            weight = Farm_Weight(
                date_filed = now(),
                ref_farm_id = farmID,
                is_starter = True,
                ave_weight = request.POST.get('ave_weight'),
                total_numHeads = farm.total_pigs,
                total_kls =  request.POST.get('total_kls'),
                remarks = request.POST.get('remarks'),
                pigpen_grp_id = latestPigpen.id
            )
            weight.save()
            messages.success(request, "Weight recorded.", extra_tags='weight')
            return redirect('/selected-health-symptoms/' + str(farmID))
        
        else:
            weight = Farm_Weight(
                date_filed = now(),
                ref_farm_id = farmID,
                is_starter = False,
                ave_weight = 0,
                total_numHeads = 0,
                total_kls =  0,
                remarks = request.POST.get('remarks'),
                pigpen_grp_id = latestPigpen.id
            )
            
            weightList = []
            pigs_sold = 0
            for i in request.POST.getlist('input-kls'):
                if i != "":
                    weight.total_kls += float(i)
                    weightList.append(Hog_Weight(
                        farm_weight = weight,
                        final_weight = round(float(i), 2)
                    ))
                    
                    pigs_sold += 1
                    farm.total_pigs = farm.total_pigs - 1

            weight.total_numHeads = pigs_sold
            weight.ave_weight = round(weight.total_kls / weight.total_numHeads, 2)

            farm.save()
            weight.save()
            Hog_Weight.objects.bulk_create(weightList)

            messages.success(request, "Weight recorded.", extra_tags='weight')
            return redirect('/selected-health-symptoms/' + str(farmID))
        
        # else:
        #     messages.error(request, "Current farm already has starter and fattener weight.", extra_tags="add-weight")

        
    weightForm = WeightForm()
    return render(request, 'healthtemp/add-weight.html', {'weightForm': weightForm, 'farmID': int(farmID), 'weightType': weightType, 'total_pigs': farm.total_pigs})


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
    mortQry = Mortality.objects.order_by("mortality_date").all()
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

        mortQry = Mortality.objects.filter(mortality_date__range=(sDate, eDate)).order_by("mortality_date").all()

        if not mortQry.exists(): # (ERROR) No Mortality records found.
            messages.error(request, "No Mortality records found.", extra_tags="mort-report")
            return render(request, 'healthtemp/rep-hogs-mortality.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})


    else: # (CASE 2) search by BOTH date range and areaName
        debug("TRACE: in else/")

        mortQry = Mortality.objects.filter(mortality_date__range=(sDate, eDate)).filter(ref_farm__area__area_name=areaName).order_by("mortality_date").all()

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


def weightRange(request):
    """
    For loading data for Highcharts (weight range)
    """

    if request.method == 'POST':

        weightSeries = []
        
        # get all areas
        areaQry = Area.objects.all()

        weight_arrLow = []
        weight_arrMed = []
        weight_arrHigh = []


        for area in areaQry:

            count_base = 0      # 0-59kg
            count_low = 0       # 60-79kg
            count_med = 0       # 80-99kg
            count_high = 0      # 100-120kg
            count_ceil = 0      # 121kg <

            farm_baseDict = {}
            farm_lowDict = {}
            farm_medDict = {}
            farm_highDict = {}
            farm_ceilDict = {}

            final_weightQry = Hog_Weight.objects.filter(farm_weight__ref_farm__area = area.id).annotate(
                farm = F("farm_weight__ref_farm")).all()

            # loop through each Farm
            for f in final_weightQry:

                # format 3-digit farm ID
                farmID = f.farm
                farmID = "Farm {id:03}".format(id = farmID)

                # classify per weight categ
                if f.final_weight in range(0, 60):
                    count_base += 1
                    try:
                        farm_baseDict.update({farmID: farm_baseDict.get(farmID) + 1})
                    except:
                        farm_baseDict.update({farmID: 1})

                elif f.final_weight in range(60, 81):
                    count_low += 1
                    try:
                        farm_lowDict.update({farmID: farm_lowDict.get(farmID) + 1})
                    except:
                        farm_lowDict.update({farmID: 1})

                elif f.final_weight in range(80, 101):
                    count_med += 1
                    try:
                        farm_medDict.update({farmID: farm_medDict.get(farmID) + 1})
                    except:
                        farm_medDict.update({farmID: 1})

                elif f.final_weight in range(101, 121):
                    count_high += 1
                    try:
                        farm_highDict.update({farmID: farm_highDict.get(farmID) + 1})
                    except:
                        farm_highDict.update({farmID: 1})
                        
                elif f.final_weight > 120:
                    count_ceil += 1
                    try:
                        farm_ceilDict.update({farmID: farm_ceilDict.get(farmID) + 1})
                    except:
                        farm_ceilDict.update({farmID: 1})

            # debug(area.area_name)

            # add in series -> (total count per weight range, [list of farm IDs within range, total count in per farm])
            weightSeries.append([area.area_name, 
                                [count_base, list(farm_baseDict.items())],
                                [count_low, list(farm_lowDict.items())],
                                [count_med, list(farm_medDict.items())],
                                [count_high, list(farm_highDict.items())],
                                [count_ceil, list(farm_ceilDict.items())]
                                ])

        # debug(weightSeries)

    return JsonResponse(weightSeries, safe=False)


def update_diseaseCase(request, dcID):
    """
    (POST-AJAX) For updating total and no. of recovered pigs of a Disease Case

    :param dcID: PK of selected Disease Case
    :type dcID: string
    """

    debug("in update_diseaseCase()/n")

    if request.method == 'POST':
        dateToday = datetime.now(timezone.utc)

        # get input from Recovered field
        numRecovered = int(request.POST.get("num_rec"))
        
        debug(numRecovered)
        debug(dcID)

        # Qry latest Disease_Record under given (1) dcID
        latestDR = Disease_Record.objects.filter(ref_disease_case=dcID).order_by("-date_filed").first()
        updateDC = Disease_Case.objects.filter(id=dcID).first()
        
        debug(latestDR.date_filed);

        if (latestDR.date_filed == dateToday.date()):

            latestDR.num_recovered = numRecovered
            latestDR.total_recovered += (numRecovered + latestDR.total_recovered)
            latestDR.save()

            # update "date_updated" of Disease Case to date-time today
            updateDC.date_updated = dateToday
            updateDC.save()

        else: # make new Disease Record for the Case if none exists today
            newDR = Disease_Record()
            newDR.num_recovered = numRecovered
            newDR.num_died = 0

            # add created record to totals
            newDR.total_recovered = (numRecovered + latestDR.total_recovered)
            newDR.total_died = latestDR.total_died

            # Qry disease case then FK whole object to disease record
            newDR.ref_disease_case = updateDC

            # update "date_updated" of Disease Case to date today
            updateDC.date_updated = dateToday
            updateDC.save()

            # save new Disease record
            newDR.save()

        # (SUCCESS) Disease record created. Send to client side (js)
        return JsonResponse({"status_code":"200"}, status=200)


    return JsonResponse({"error": "not an AJAX post request"}, status=400)
from os import getenv
from threading import activeCount
from xmlrpc.client import Boolean
from django.contrib.auth.models import User
from django.db.models import (
    F,Q,
    Case,
    When,
    Value)
from django.forms.formsets import formset_factory

# for page redirection, server response
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, response
# for AJAX functions
from django.http import JsonResponse
from django.core import serializers
import json
from twilio.rest import Client

# for Forms
from .forms import (
    HogRaiserForm, 
    FarmForm, 
    PigpenRowForm,
    ActivityForm, 
    AreaForm, 
    MemAnnouncementForm
)
from django.forms import formset_factory

# Geocoding
from geopandas.tools import (
    geocode,
    reverse_geocode
    )

# for storing success and error Django messages
from django.contrib import messages

# for Model imports
from .models import (
    Area, 
    AccountData,
    ExternalBiosec,
    Farm_Weight, 
    InternalBiosec, 
    Farm, 
    Hog_Raiser,
    Mortality,
    Pigpen_Group, 
    Pigpen_Row,
    Activity, 
    Mem_Announcement,
    Activities_Form,
    Hog_Symptoms,
    Mortality_Form
)
from django.db.models.functions import Concat

# from other apps
from healthapp.views import compute_MortRate

# import regex
import re

#Creating a cursor object using the cursor() method
# from django.shortcuts import render

# for date and time fields in Models
from datetime import date, datetime, timezone, timedelta
from django.utils.timezone import (
    make_aware, # for date and time fields in Models
    now, # for getting date today
    localtime, # for getting date today
    timedelta
) 

# for list comapare
from collections import Counter
from pprint import pprint
def debug(m):
    """
    For debugging purposes

    :param m: The message
    :type m: String
    """
    print("------------------------[DEBUG]------------------------")
    
    
    try:
        pprint(m)
    except:
        try:
            print(m)
        except:
            print("---------------------[Print_ERROR]---------------------")
        else:     
            print("--------------------[Print_SUCCESS]--------------------")
        return
        
    print("--------------------[Print_SUCCESS]--------------------")

def debugFunc(func, message):
    print("-----------------------------[{}]------------------------START".format(str(message).upper()))
    func()
    print("-----------------------------[{}]-------------------------STOP ".format(str(message).upper()))

# Farms Management Module Views

def getMapData(request):
    if request.method == 'POST':
        data = []
        qry = Farm.objects.select_related('hog_raiser', 'area').annotate(
                fname=F("hog_raiser__fname"), 
                lname=F("hog_raiser__lname"), 
                contact=F("hog_raiser__contact_no"),
                farm_area = F("area__area_name")
                ).values(
                    "id", 
                    "loc_lat",
                    "loc_long", 
                    "total_pigs",
                    "farm_address",
                    "last_updated"
                    )
        for f in qry:
            morts = 0
            for mort in Mortality.objects.filter(ref_farm_id = f["id"]).filter(mortality_date__range=(now() - timedelta(days=120), now())).values("num_today"):
                morts += mort["num_today"]
            farmObject = {
                "code":  str(f["id"]),
                "latitude": f["loc_lat"],
                "longitude": f["loc_long"],
                "numPigs": str(f["total_pigs"]),
                "address": f["farm_address"],
                "mortRts": compute_MortRate(f["id"], None),
                "morts": morts,
                "sxRept": Hog_Symptoms.objects.filter(ref_farm_id=f["id"]).filter(date_updated__range=(now() - timedelta(days=120), now())).count(),
                "sxActv": Hog_Symptoms.objects.filter(ref_farm_id=f["id"]).filter(report_status="Active").filter(date_updated__range=(now() - timedelta(days=120), now())).count(),
                "latest": f["last_updated"]
            }
            data.append(farmObject)
    return JsonResponse(data, safe=False)

## Farms table for all users except Technicians
def farms(request):
    """
    Display all farms for assistant manager
    """

    # TODO get areas for filter
    qry = Farm.objects.select_related('hog_raiser', 'area', 'extbio').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        mem_code=F("hog_raiser__mem_code"), 
        contact=F("hog_raiser__contact_no"),
        farm_area = F("area__area_name"),
        last_update = F("extbio__last_updated")
        ).values(
            "id",
            "fname",
            "lname", 
            "mem_code",
            "contact", 
            "farm_address",
            "farm_area",
            "total_pigs",
            "num_pens",
            "last_update"
            ).order_by('total_pigs')
    # debug(qry)
    
    farmsData = []
    for f in qry:
        farmObject = {
            "code":  f["id"],
            "raiser": " ".join((f["fname"],f["lname"])),
            "mem_code": f["mem_code"],
            "contact": f["contact"],
            "address": f["farm_address"],
            "area": str(f["farm_area"]),
            "pigs": str(f["total_pigs"]),
            "pens": str(f["num_pens"]),
            "updated": f["last_update"]
        }
        farmsData.append(farmObject)

        sorted_FarmsList = sorted(farmsData, key = lambda i: i['pigs'], reverse=True)
        # sorted_FarmsList = sorted(sorted(farmsData, key = lambda i: i['pigs'], reverse=True), key = lambda i: i['updated'], reverse=False)


    areaList = []
    for choice in Area.objects.distinct().order_by('area_name').values('area_name'):
            areaList.append({"area_name": choice['area_name']})

    memList = []
    for mem in Hog_Raiser.objects.distinct().order_by('mem_code').values('mem_code'):
        if mem['mem_code'] is not None:
            memList.append(mem['mem_code'])

    # debug(memList)

    # debug(farmsData)
    return render(request, 'farmstemp/farms.html', {"farms":sorted_FarmsList, "areaList":areaList, "memList":memList}) ## Farms table for all users except Technicians

def selectedFarm(request, farmID):
    """
    Display information of selected farm for assistant manager

    :param farmID: PK of selected farm
    :type farmID: integer
    """

    # get total num. of pigs in farm
    farmPigs = Farm.objects.filter(id=farmID).only("total_pigs").first()

    # collect pigpens
    latestPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()
    pigpenQry = Pigpen_Row.objects.filter(pigpen_grp_id=latestPigpen.id).order_by("id")

    pen_no = 1
    pigpenList = []
    total_heads = 0
    for pen in pigpenQry:
        pigpenObj = {
            'pen_no' : pen_no,
            'length' : pen.length,
            'width' : pen.width,
            'num_heads' : pen.num_heads
        }
        
        total_heads += pen.num_heads
        pigpenList.append(pigpenObj)
        pen_no += 1

    # get final weight slip
    final_weight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=latestPigpen.id).last()

    # convert Date range to datetime type; then to a timezone-aware datetime
    sDate = make_aware(datetime.combine(latestPigpen.date_added, datetime.min.time()))
    debug("sDate: " + str(sDate) + " TYPE -- " + str(type(sDate)))

    # collect activities
    if farmPigs.total_pigs == 0:
        #--- DEBUG
        eDate = make_aware(datetime.combine(final_weight.date_filed, datetime.min.time()))
        debug("eDate: " + str(eDate) + " TYPE -- " + str(type(eDate)))
        #---

        actQuery = Activity.objects.filter(ref_farm_id=farmID).filter(is_approved=True).filter(date__range=(latestPigpen.date_added, final_weight.date_filed)).all().order_by('-date')
    
        # get farm based on farmID; get related data from hog_raisers, extbio, and intbio
        qry = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'intbio', 'extbio').annotate(
            raiser          = Concat('hog_raiser__fname', Value(' '), 'hog_raiser__lname'),
            raiser_mem_code = F("hog_raiser__mem_code"),
            contact         = F("hog_raiser__contact_no"),
            length          = F("wh_length"),
            width           = F("wh_width"),
            farm_area       = F("area__area_name"),
            waste_mgt       = F("intbio__waste_mgt"),
            isol_pen        = F("intbio__isol_pen"),
            bird_proof      = F("extbio__bird_proof"),
            perim_fence     = F("extbio__perim_fence"),
            foot_dip        = F("intbio__foot_dip"),
            fiveh_m_dist    = F("extbio__fiveh_m_dist"))
    else:
        eDate = now()
        actQuery = Activity.objects.filter(ref_farm_id=farmID).filter(is_approved=True).filter(date__range=(latestPigpen.date_added, now())).all().order_by('-date')

        # get farm based on farmID; get related data from hog_raisers, extbio, and intbio
        qry = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'intbio', 'extbio').annotate(
            raiser          = Concat('hog_raiser__fname', Value(' '), 'hog_raiser__lname'),
            raiser_mem_code = F("hog_raiser__mem_code"),
            contact         = F("hog_raiser__contact_no"),
            length          = F("wh_length"),
            width           = F("wh_width"),
            farm_area       = F("area__area_name"),
            waste_mgt       = F("intbio__waste_mgt"),
            isol_pen        = F("intbio__isol_pen"),
            bird_proof      = F("extbio__bird_proof"),
            perim_fence     = F("extbio__perim_fence"),
            foot_dip        = F("intbio__foot_dip"),
            fiveh_m_dist    = F("extbio__fiveh_m_dist"))

    # debug(qry)

    # pass all data from Qry into an object
    selectedFarm = qry.values(
        "id",
        "raiser",
        "raiser_mem_code",
        "contact",
        "directly_manage",
        "farm_address",
        "farm_area",
        "roof_height",
        "wh_length", 
        "wh_width",
        "total_pigs",
        "feed_trough",
        "bldg_cap",
        "medic_tank",
        "bldg_curtain",
        "road_access",
        "waste_mgt",
        "isol_pen",
        "bird_proof",
        "perim_fence",
        "foot_dip",
        "fiveh_m_dist",
    ).first()

    # debug(selectedFarm)

    # collecting all past pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()

    versionList = []
    for pen in allPigpens:
        fWeight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=pen.id).last()
        # debug(fWeight.date_filed)

        if latestPigpen.id == pen.id and farmPigs.total_pigs == 0:
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


    actList = []

    # store all data to an array
    for activity in actQuery:
        actList.append({
            'id' : activity.id,
            'date' : activity.date,
            'trip_type' : activity.trip_type,
            'time_arrival' : activity.time_arrival,
            'time_departure' : activity.time_departure,
            'num_pigs_inv' : activity.num_pigs_inv,
            'remarks' : activity.remarks,
        })

    # collect biosecurity checklists
    # Select Biochecklist with latest date
    currbioQuery = Farm.objects.filter(id=farmID).filter(intbio__last_updated__range=(sDate, eDate)).select_related('intbio').select_related('extbio').all()

    # Get latest instance of Biochecklist
    currbioObj = currbioQuery.first()

    # Get all biosecID, last_updated in extbio under a Farm
    extQuery = ExternalBiosec.objects.filter(ref_farm_id=farmID).filter(last_updated__range=(sDate, eDate)).only(
        'last_updated',
    ).order_by('-last_updated')

    return render(request, 'farmstemp/selected-farm.html', {'farm' : selectedFarm, 'pigpens' : pigpenList, 'activity' : actList, 'currBio': currbioObj, 'fattener' : final_weight,
                                                            'bioList': extQuery, 'version' : versionList, 'selectedPigpen' : latestPigpen, 'latest' : latestPigpen, 'total_heads' : total_heads})

def selectedFarmVersion(request, farmID, farmVersion):
    """
    Display information of selected farm for assistant manager

    :param farmID: PK of selected farm
    :type farmID: integer
    """

    # get total num. of pigs in farm
    farmPigs = Farm.objects.filter(id=farmID).only("total_pigs").first()

    # collect pigpens
    selectedPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).filter(id=farmVersion).first()
    pigpenQry = Pigpen_Row.objects.filter(pigpen_grp_id=selectedPigpen.id).order_by("id")

    pen_no = 1
    pigpenList = []
    total_heads = 0
    for pen in pigpenQry:
        pigpenObj = {
            'pen_no' : pen_no,
            'length' : pen.length,
            'width' : pen.width,
            'num_heads' : pen.num_heads }
        
        total_heads += pen.num_heads
        pigpenList.append(pigpenObj)
        pen_no += 1


    # get final weight slip
    final_weight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=selectedPigpen.id).last()

    lastPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()

    sDate = make_aware(datetime.combine(selectedPigpen.date_added, datetime.min.time()))
    debug("sDate: " + str(sDate) + " TYPE -- " + str(type(sDate)))

    # collect activities
    if final_weight is not None:
        actQuery = Activity.objects.filter(ref_farm_id=farmID).filter(is_approved=True).filter(date__range=(selectedPigpen.date_added, final_weight.date_filed)).all().order_by('-date')

        eDate = make_aware(datetime.combine(final_weight.date_filed, datetime.min.time()))
        debug("eDate: " + str(eDate) + " TYPE -- " + str(type(eDate)))

        # get farm based on farmID; get related data from hog_raisers, extbio, and intbio
        qry = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'internalbiosec', 'externalbiosec').annotate(
            raiser          = Concat('hog_raiser__fname', Value(' '), 'hog_raiser__lname'),
            raiser_mem_code = F("hog_raiser__mem_code"),
            contact         = F("hog_raiser__contact_no"),
            length          = F("wh_length"),
            width           = F("wh_width"),
            farm_area       = F("area__area_name"),
            waste_mgt       = F("intbio__waste_mgt"),
            isol_pen        = F("intbio__isol_pen"),
            bird_proof      = F("extbio__bird_proof"),
            perim_fence     = F("extbio__perim_fence"),
            foot_dip        = F("intbio__foot_dip"),
            fiveh_m_dist    = F("extbio__fiveh_m_dist"))
    else:
        actQuery = Activity.objects.filter(ref_farm_id=farmID).filter(is_approved=True).filter(date__range=(selectedPigpen.date_added, now())).all().order_by('-date')

        #--- DEBUG
        eDate = now()
        debug("eDate: " + str(eDate) + " TYPE -- " + str(type(eDate)))
        #---

        # get farm based on farmID; get related data from hog_raisers, extbio, and intbio
        qry = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'internalbiosec', 'externalbiosec').annotate(
            raiser          = Concat('hog_raiser__fname', Value(' '), 'hog_raiser__lname'),
            raiser_mem_code = F("hog_raiser__mem_code"),
            contact         = F("hog_raiser__contact_no"),
            length          = F("wh_length"),
            width           = F("wh_width"),
            farm_area       = F("area__area_name"),
            waste_mgt       = F("intbio__waste_mgt"),
            isol_pen        = F("intbio__isol_pen"),
            bird_proof      = F("extbio__bird_proof"),
            perim_fence     = F("extbio__perim_fence"),
            foot_dip        = F("intbio__foot_dip"),
            fiveh_m_dist    = F("extbio__fiveh_m_dist"))
        
    # debug(qry)

    # pass all data into an object
    selectedFarm = qry.values(
        "id",
        "raiser",
        "raiser_mem_code",
        "contact",
        "directly_manage",
        "farm_address",
        "farm_area",
        "roof_height",
        "wh_length", 
        "wh_width",
        "total_pigs",
        "feed_trough",
        "bldg_cap",
        "medic_tank",
        "bldg_curtain",
        "road_access",
        "waste_mgt",
        "isol_pen",
        "bird_proof",
        "perim_fence",
        "foot_dip",
        "fiveh_m_dist",
    ).first()
   
    # debug(selectedFarm)

    # collecting all past pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()

    versionList = []
    for pen in allPigpens:
        fWeight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=pen.id).last()
        # debug(fWeight.date_filed)

        if selectedPigpen.id == pen.id and farmPigs.total_pigs == 0:
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


    actList = []

    # store all data to an array
    for activity in actQuery:
        actList.append({
            'id' : activity.id,
            'date' : activity.date,
            'trip_type' : activity.trip_type,
            'time_arrival' : activity.time_arrival,
            'time_departure' : activity.time_departure,
            'num_pigs_inv' : activity.num_pigs_inv,
            'remarks' : activity.remarks,
        })

    # collect biosecurity checklists
    # Select Biochecklist with latest date
    currbioQuery = Farm.objects.filter(id=farmID).filter(intbio__last_updated__range=(sDate, eDate)).select_related('intbio').select_related('extbio').all()
    
    # Get latest instance of Biochecklist
    currbioObj = currbioQuery.first()

    # Get all biosecID, last_updated in extbio under a Farm
    extQuery = ExternalBiosec.objects.filter(ref_farm_id=farmID).filter(last_updated__range=(sDate, eDate)).only(
        'last_updated',
    ).order_by('-last_updated')


    return render(request, 'farmstemp/selected-farm.html', {'farm' : selectedFarm, 'pigpens' : pigpenList, 'activity' : actList, 'currBio': currbioObj, 'latest' : lastPigpen,
                                                            'bioList': extQuery, 'version' : versionList, 'selectedPigpen' : selectedPigpen, 'fattener' : final_weight, 'total_heads' : total_heads})


def techFarms(request):
    """
    - Display all farms under areas assigned to currently logged in technician. 
    """
    
    # get all farms under the current technician 
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all().order_by('id')
    areaNum = len(areaQry)
    areaNames = []

    # array to store all farms under each area
    techFarmsList = []
    sorted_techFarmsList = []
    
    # collect all farms under each area
    for area in areaQry :
        areaNames.append(area.area_name)

        # collect the corresponding hog raiser details for each farm 
        techFarmQry  = Farm.objects.filter(area_id=area.id).select_related('hog_raiser','extbio').annotate(
                    fname=F("hog_raiser__fname"), lname=F("hog_raiser__lname"), contact=F("hog_raiser__contact_no"),
                    last_update = F("extbio__last_updated")).values(
                            "id",
                            "fname",
                            "lname", 
                            "contact", 
                            "farm_address",
                            "last_update", 
                            "total_pigs")


        # pass all data into an array
        for farm in techFarmQry:
            
            farmObject = {
                "area" : area.area_name,
                "code": farm["id"],
                "raiser": " ".join((farm["fname"],farm["lname"])),
                "contact": farm["contact"],
                "address": farm["farm_address"],
                "updated": farm["last_update"],
                "pigs" : farm["total_pigs"] }

            techFarmsList.append(farmObject)
        
        sorted_techFarmsList = sorted(techFarmsList, key = lambda i: i['pigs'], reverse=True)
        # sorted_techFarmsList = sorted(sorted_byPigs, key = lambda i: i['updated'], reverse=False)
    
    if sorted_techFarmsList is not None:
        techData = {
            "techFarms" : sorted_techFarmsList,
            "areaCount" : areaNum,
            "areaString" : ', '.join(areaNames) }
    
    else :
        techData = {
            "techFarms" : techFarmsList,
            "areaCount" : areaNum,
            "areaString" : ', '.join(areaNames) }

    return techData

def techSelectedFarm(request, farmID):
    """
    - Display details of the selected farm under the currently logged in technician.
    - Will collect the hog raiser, area, internal and external biosecurity, and pigpen measures connected to the farm.   
    farmID - selected farmID passed as parameter
    """

    ## get details of selected farm
    # collect the corresponding details for: hog raiser, area, internal and external biosecurity
    techFarmQry = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'intbio', 'extbio').annotate(
                    raiser      = Concat('hog_raiser__fname', Value(' '), 'hog_raiser__lname'),
                    raiser_mem_code=F("hog_raiser__mem_code"),
                    contact     = F("hog_raiser__contact_no"),
                    farm_area   = F("area__area_name"),
                    waste_mgt   = F("intbio__waste_mgt"),
                    isol_pen    = F("intbio__isol_pen"),
                    bird_proof  = F("extbio__bird_proof"),
                    perim_fence = F("extbio__perim_fence"),
                    foot_dip    = F("intbio__foot_dip"),
                    fiveh_m_dist = F("extbio__fiveh_m_dist"))

    # pass all data into an object
    selTechFarm = techFarmQry.values(
        "id",
        "raiser",
        "raiser_mem_code",
        "contact",
        "directly_manage",
        "farm_address",
        "farm_area",
        "roof_height",
        "wh_length", 
        "wh_width",
        "total_pigs",
        "feed_trough",
        "bldg_cap",
        "medic_tank",
        "bldg_curtain",
        "road_access",
        "waste_mgt",
        "isol_pen",
        "bird_proof",
        "perim_fence",
        "foot_dip",
        "fiveh_m_dist",
    ).first()

    # collect the corresponding pigpens for selected farm
    latestPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()
    pigpenQry = Pigpen_Row.objects.filter(pigpen_grp_id=latestPigpen.id).order_by("id")

    # get current starter and fattener weights acc. to current Pigpen
    # weightSlip = Pigpen_Group.objects.filter(id=latestPigpen.id).select_related("start_weight").select_related("final_weight").first()
    start_weight = Farm_Weight.objects.filter(is_starter=True).filter(pigpen_grp_id=latestPigpen.id).first()
    final_weight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=latestPigpen.id).last()

    pen_no = 1
    pigpenList = []
    total_heads = 0
    for pen in pigpenQry:
        pigpenObj = {
            'pen_no' : pen_no,
            'length' : pen.length,
            'width' : pen.width,
            'num_heads' : pen.num_heads
        }
        
        total_heads += pen.num_heads
        pigpenList.append(pigpenObj)
        pen_no += 1


    # collecting all past pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()

    versionList = []
    for pen in allPigpens:
        fWeight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=pen.id).last()
        # debug(fWeight.date_filed)

        if latestPigpen.id == pen.id and int(selTechFarm.get('total_pigs')) == 0:
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

    # adding new pigpens
    if request.method == 'POST':
        print("TEST LOG: Form has POST method") 
        print(request.POST)

        pigpenRowForm = PigpenRowForm(request.POST)   
        currFarm = Farm.objects.filter(id=farmID).first()

        # pass all pigpens values into array newPigpenList
        newPigpenList = []

        i = 0
        for num_heads in request.POST.getlist('num_heads', default=None):
            pigpenObj = {
                "length" : request.POST.getlist('length', default=None)[i],
                "width" : request.POST.getlist('width', default=None)[i],
                "num_heads" : request.POST.getlist('num_heads', default=None)[i],
            }

            newPigpenList.append(pigpenObj)
            i += 1
        
        if pigpenRowForm.is_valid():

            # create instance of Pigpen_Group model
            pigpen_group = Pigpen_Group.objects.create(
                date_added = datetime.now(timezone.utc),
                ref_farm = currFarm
            )

            pigpen_group.save()
                        
            # temporary variable to store total of all num_heads
            numTotal = 0 
    
            # pass all newPigpenList objects into Pigpen_Row model
            x = 0
            
            for pigpen in newPigpenList:
                pigpen = newPigpenList[x]

                # create new instance of Pigpen_Row model
                pigpen_measure = Pigpen_Row.objects.create(
                    pigpen_grp_id = pigpen_group.id,
                    length = pigpen['length'],
                    width = pigpen['width'],
                    num_heads = pigpen['num_heads'],
                )
                
                # add all num_heads (pigpen measure) for total_pigs (farm)
                numTotal += int(pigpen_measure.num_heads)
                pigpen_measure.save()
                x += 1

            # update num_pens and total_pigs of newly added farm
            currFarm.num_pens = len(newPigpenList)
            currFarm.total_pigs = numTotal
            currFarm.save()

            pigpen_group.num_pens = len(newPigpenList)
            pigpen_group.total_pigs = numTotal
            pigpen_group.save()
            
            messages.success(request, str(len(newPigpenList)) + " new pigpens successfully added.", extra_tags='add-farm' + str(farmID))
            return redirect('/tech-selected-farm/' + str(farmID))

        else:
            print("TEST LOG: Pigpen Measures Form not valid")
            print(pigpenRowForm.errors)

            messages.error(request, "Error adding farm. " + str(pigpenRowForm.errors), extra_tags='add-farm')
    else:
        print("TEST LOG: Form is not a POST method")

        # if the forms have no input yet, only display empty forms
        pigpenRowForm  = PigpenRowForm()

    # pass (1) delected farm + biosecurity details, and (2) pigpen measures object to template   
    return render(request, 'farmstemp/tech-selected-farm.html', {'farm' : selTechFarm, 'pigpens' : pigpenList, 'pigpenRowForm' : pigpenRowForm, 'starter' : start_weight, 'total_heads' : total_heads,
                                                                'version' : versionList, 'selectedPigpen' : latestPigpen, 'latest' : latestPigpen, 'fattener' : final_weight})

def techSelectedFarmVersion(request, farmID, farmVersion):
    """
    - Display details of the selected farm under the currently logged in technician.
    - Will collect the hog raiser, area, internal and external biosecurity, and pigpen measures connected to the farm.   
    farmID - selected farmID passed as parameter
    farmVersion - id of the selected farm version
    """

    ## get details of selected farm
    # collect the corresponding details for: hog raiser, area, internal and external biosecurity
    techFarmQry = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'intbio', 'extbio').annotate(
                    raiser      = Concat('hog_raiser__fname', Value(' '), 'hog_raiser__lname'),
                    raiser_mem_code = F("hog_raiser__mem_code"), 
                    contact     = F("hog_raiser__contact_no"),
                    farm_area   = F("area__area_name"),
                    waste_mgt   = F("intbio__waste_mgt"),
                    isol_pen    = F("intbio__isol_pen"),
                    bird_proof  = F("extbio__bird_proof"),
                    perim_fence = F("extbio__perim_fence"),
                    foot_dip    = F("intbio__foot_dip"),
                    fiveh_m_dist = F("extbio__fiveh_m_dist"))

    # pass all data into an object
    selTechFarm = techFarmQry.values(
        "id",
        "raiser",
        "raiser_mem_code",
        "contact",
        "directly_manage",
        "farm_address",
        "farm_area",
        "roof_height",
        "wh_length", 
        "wh_width",
        "total_pigs",
        "feed_trough",
        "bldg_cap",
        "medic_tank",
        "bldg_curtain",
        "road_access",
        "waste_mgt",
        "isol_pen",
        "bird_proof",
        "perim_fence",
        "foot_dip",
        "fiveh_m_dist",
    ).first()

    # collect the corresponding pigpens for selected farm
    selectedPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).filter(id=farmVersion).first()
    pigpenQry = Pigpen_Row.objects.filter(pigpen_grp_id=selectedPigpen.id).order_by("id")

    # get current starter and fattener weights acc. to selected Pigpen
    # weightSlip = Pigpen_Group.objects.filter(id=selectedPigpen.id).select_related("start_weight").select_related("final_weight").first()
    start_weight = Farm_Weight.objects.filter(is_starter=True).filter(pigpen_grp_id=selectedPigpen.id).first()
    final_weight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=selectedPigpen.id).last()

    pen_no = 1
    pigpenList = []
    total_heads = 0
    for pen in pigpenQry:
        pigpenObj = {
            'pen_no' : pen_no,
            'length' : pen.length,
            'width' : pen.width,
            'num_heads' : pen.num_heads }

        total_heads += pen.num_heads
        pigpenList.append(pigpenObj)
        pen_no += 1

    lastPigpen = Pigpen_Group.objects.filter(ref_farm_id=farmID).last()

    # collecting all past pigpens
    allPigpens = Pigpen_Group.objects.filter(ref_farm_id=farmID).order_by("-id").all()

    versionList = []
    for pen in allPigpens:
        fWeight = Farm_Weight.objects.filter(is_starter=False).filter(pigpen_grp_id=pen.id).last()

        if selectedPigpen.id == pen.id and int(selTechFarm.get('total_pigs')) == 0:
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
        
    return render(request, 'farmstemp/tech-selected-farm.html', {'farm' : selTechFarm, 'pigpens' : pigpenList, 'version' : versionList, 'starter' : start_weight,
                                                                'selectedPigpen' : selectedPigpen, 'latest' : lastPigpen, 'fattener' : final_weight, 'total_heads' : total_heads })

def addFarm(request):
    """
    - Redirect to Add Farm Page and render corresponding Django forms
    - Add new farm to database 
    - Save details to hog_raiser, pigpen_measure, and externalbiosec and internalbiosec tables
    - Django forms will first check the validity of input (based on the fields within models.py)
    - Collect input for internal and external biosec and create new instance to be saved as FK for new farm
    - Save new input for hog raiser but if raiser exists, collect existing raiser ID
    """
    
    latestFarm = Farm.objects.last()
    try:
        farmID = int(latestFarm.id) + 1
    except:
        farmID = 1
    # print(farmID)

    # get all hog raisers to be passed as dropdown
    hogRaiserQry = Hog_Raiser.objects.all().order_by('lname')

    # get current user (technician) ID
    techID = request.user.id

    # collect all assigned areas under technician; to be passed to template
    areaQry = Area.objects.filter(tech_id=techID)

    if request.method == 'POST':
        print("addFarm: Form has POST method") 
        print(request.POST)

        areaName = request.POST.get("input-area", None)

        # get ID of selected area
        areaIDQry = Area.objects.filter(area_name=areaName).first()
        areaID = areaIDQry.id

        # render forms
        hogRaiserForm       = HogRaiserForm(request.POST)
        farmForm            = FarmForm(request.POST)
        pigpenRowForm       = PigpenRowForm(request.POST)   
        
        # validate django farm and pigpen forms
        if farmForm.is_valid():
            farm = farmForm.save(commit=False)

            # FARM ADDRESS
            street = request.POST.get("address-street", None)
            barangay = request.POST.get("address-barangay", None)
            city = request.POST.get("address-city", None)
            province = request.POST.get("address-province", None)
            zipcode = request.POST.get("address-zipcode", None)

            addressList = [street, barangay, city, province, zipcode, "Philippines"]
            farmAddress = ", ".join(filter(None, addressList))
            farm.farm_address = farmAddress

            try:
                farmAddress = ", ".join(filter(None, addressList))
                debug(farmAddress)
                farmLoc = geocode([farmAddress]).geometry.iloc[0]
                if farmLoc.x != 0 and farmLoc.y != 0:
                    farm.loc_long = farmLoc.x
                    farm.loc_lat = farmLoc.y

                    # save hog raiser
                    raiserID = request.POST.get("input-exist-raiser", None)

                    if raiserID == None or raiserID == "" :

                        # if empty, new raiser is inputted; validate django hog raiser form
                        if hogRaiserForm.is_valid():
                            hogRaiser = hogRaiserForm.save(commit=False)
                            hogRaiser.contact_no = str("63") + str(hogRaiser.contact_no)
                            # print(hogRaiser.contact_no)

                            hogRaiser.save()
                            print("addFarm: Added new raiser")

                            # save raiser ID to farm
                            farm.hog_raiser = hogRaiser
                        
                        else:
                            print("addFarm: Hog Raiser Form not valid. No input added.")
                            print(hogRaiserForm.errors)

                            messages.error(request, "Error adding farm. " + str(hogRaiserForm.errors))

                    else:
                        # find selected raiser id
                        hogRaiser = Hog_Raiser.objects.filter(id=raiserID)

                        # save raiser ID to farm
                        farm.hog_raiser_id = raiserID

                    # collect internal biosec checkbox inputs and convert to integer value
                    if request.POST.get("cb-isolation", None) == 'on':
                        isol_pen = 0
                    else :
                        isol_pen = 1

                    if request.POST.get("cb-footdip", None) == 'on':
                        foot_dip = 0
                    else :
                        foot_dip = 1

                    # create new instance of InternalBiosec model and pass converted checkbox inputs
                    internalBiosec = InternalBiosec.objects.create(
                        isol_pen = isol_pen,
                        foot_dip = foot_dip,
                        waste_mgt = request.POST.get("waste-mgt", None)
                    )

                    # collect external biosec checkbox inputs and convert to integer value
                    if request.POST.get("cb-birdproof", None) == 'on':
                        bird_proof = 0
                    else :
                        bird_proof = 1

                    if request.POST.get("cb-fence", None) == 'on':
                        perim_fence = 0
                    else :
                        perim_fence = 1

                    if request.POST.get("cb-distance", None) == 'on':
                        fiveh_m_dist = 0
                    else :
                        fiveh_m_dist = 1

                    # create new instance of ExternalBiosec model and pass converted checkbox inputs
                    externalBiosec = ExternalBiosec.objects.create(
                        bird_proof = bird_proof,
                        perim_fence = perim_fence,
                        fiveh_m_dist = fiveh_m_dist
                    )


                    # pass data as FKs for farm
                    farm.extbio = externalBiosec
                    farm.intbio = internalBiosec
                    farm.area_id = areaID
                    farm.id = farmID

                    farm.save()
                    print("addFarm: Added new farm")
                    messages.success(request, "Farm " + str(farm.id) + " has been successfully added.", extra_tags='add-farm' + str(farm.id))

                    # get recently created internal and external biosec IDs and update ref_farm_id
                    externalBiosec.ref_farm_id = farm
                    internalBiosec.ref_farm_id = farm

                    internalBiosec.save()
                    externalBiosec.save()

                    if pigpenRowForm.is_valid():
                        
                        # create instance of Pigpen_Group model
                        pigpen_group = Pigpen_Group.objects.create(
                            date_added = datetime.now(timezone.utc),
                            ref_farm = farm
                        )

                        pigpen_group.save()

                        # pass all pigpens values into array pigpenList
                        pigpenList = []

                        i = 0
                        for num_heads in request.POST.getlist('num_heads', default=None):
                            pigpenObj = {
                                "length" : request.POST.getlist('length', default=None)[i],
                                "width" : request.POST.getlist('width', default=None)[i],
                                "num_heads" : request.POST.getlist('num_heads', default=None)[i],
                            }

                            pigpenList.append(pigpenObj)
                            i += 1
                            
                        # temporary variable to store total of all num_heads
                        numTotal = 0 
                
                        # pass all pigpenList objects into Pigpen_Row model
                        x = 0
                        
                        for pigpen in pigpenList:
                            pigpen = pigpenList[x]

                            # create new instance of Pigpen_Row model
                            pigpen_measure = Pigpen_Row.objects.create(
                                pigpen_grp_id = pigpen_group.id,
                                length = pigpen['length'],
                                width = pigpen['width'],
                                num_heads = pigpen['num_heads'],
                            )
                            
                            # add all num_heads (pigpen measure) for total_pigs (farm)
                            numTotal += int(pigpen_measure.num_heads)
                            pigpen_measure.save()
                            x += 1
                        
                        # update num_pens and total_pigs of newly added farm
                        farm.num_pens = len(pigpenList)
                        farm.total_pigs = numTotal
                        farm.save()

                        pigpen_group.num_pens = len(pigpenList)
                        pigpen_group.total_pigs = numTotal
                        pigpen_group.save()

                        return redirect('/', {'farm.id': str(farm.id)})

                    else:
                        print("addFarm: Pigpen Measures Form not valid")
                        print(pigpenRowForm.errors)

                        messages.error(request, "Error adding farm. " + str(pigpenRowForm.errors))
                else: 
                    debug("farmLoc not obtained")
                    messages.error(request, "Farm location not obtained.")
            except:
                debug("farmLoc not obtained")
                messages.error(request, "Farm location not obtained.")
        
        else:
            print("addFarm: Farm Form not valid")
            print(farmForm.errors)

            messages.error(request, "Error adding farm. " + str(farmForm.errors))
     
    else:
        print("addFarm: Form is not a POST method")

        # if the forms have no input yet, only display empty forms
        hogRaiserForm       = HogRaiserForm()
        farmForm            = FarmForm()
        pigpenRowForm       = PigpenRowForm()

    # pass django forms to template
    return render(request, 'farmstemp/add-farm.html', { 'farmCode' : farmID,
                                                        'area' : areaQry,
                                                        'raisers' : hogRaiserQry,
                                                        'hogRaiserForm' : hogRaiserForm,
                                                        'farmForm' : farmForm,
                                                        'pigpenRowForm' : pigpenRowForm })

# (POST-AJAX) For searching a Biosec Checklist based on biosecID
def search_bioChecklist(request, biosecID):
    """
    (POST-AJAX) For searching a Biosecurity Checklist based on biosecID.
    """

    if request.method == 'POST':
        # print("TEST LOG: in search_bioChecklist()")

        # Get biosecID passed from AJAX URL param 
        bioID = biosecID 

        if bioID is None:
            # (ERROR) Invalid or null biosecID
            debug("(ERROR) Invalid or null biosecID")
            # messages.error(request, "Invalid biosecurity ID.", extra_tags='search-checklist')
            return JsonResponse({"error": "Invalid biosecurity ID."}, status=400)
            
        else:
            # debug("in search_bioChecklist(): bioID -- " + str(bioID))

            # SELECT id,<checklist fields from EXTERNAL>,<checklist fields from INTERNAL>
            # FROM ExternalBiosec, InternalBiosec 
            # WHERE id=bioID

            # Must be filtered by biosecID only, since bioIDs passed in dropdown is w/in Farm
            ext = ExternalBiosec.objects.filter(id=bioID).only(
                'prvdd_foot_dip',      
                'prvdd_alco_soap',     
                'obs_no_visitors',     
                'prsnl_dip_footwear',  
                'prsnl_sanit_hands',   
                'chg_disinfect_daily'
            )

            inter = InternalBiosec.objects.filter(id=bioID).only(
                'disinfect_prem',      
                'disinfect_vet_supp',     
            )

            isEditable = False

            if ext.exists() and inter.exists():
                # Get first instance in biosec queries
                ext = ext.first()
                inter = inter.first()

                # for checking if Checklist is w/in 1 day
                checkDateDiff = datetime.now(timezone.utc) - ext.last_updated

                # debug("checkDateDiff.days -- " + str(checkDateDiff.days))

                if not checkDateDiff.days > 1: # (SUCCESS) Checklist is w/in 1 day. Can still be editable
                    isEditable = True

                # Format int-ext biosec fields in a dictionary
                bioDict = {

                    'isEditable'            : isEditable,

                    # External bio
                    'prvdd_foot_dip'        : ext.prvdd_foot_dip,  
                    'prvdd_alco_soap'       : ext.prvdd_alco_soap,     
                    'obs_no_visitors'       : ext.obs_no_visitors,     
                    'prsnl_dip_footwear'    : ext.prsnl_dip_footwear,  
                    'prsnl_sanit_hands'     : ext.prsnl_sanit_hands,   
                    'chg_disinfect_daily'   : ext.chg_disinfect_daily,

                    # Internal bio
                    'disinfect_prem'        : inter.disinfect_prem,
                    'disinfect_vet_supp'    : inter.disinfect_vet_supp,   
                }

                # Serialize dictionary
                jsonStr = json.dumps(bioDict)

                # (SUCCESS) Send to client side (js)
                return JsonResponse({"instance": jsonStr}, status=200)
            else:
                # (ERROR) Internal/External Biosecurity not found.
                debug("(ERROR) Internal/External Biosecurity not found.")
                # messages.error(request, "Invalid biosecurity ID.", extra_tags='search-checklist')
                return JsonResponse({"error": "Biosecurity record not found"}, status=400)

    return JsonResponse({"error": "in search_Checklist() -- not an AJAX POST request"}, status=400)
      
# (POST-AJAX) For updating a Biosec Checklist based on biosecID
def update_bioChecklist(request, biosecID):
    """
    (POST-AJAX) For updating a Biosec Checklist based on biosecID
    """

    if request.method == 'POST':
        # print("TEST LOG: in update_bioChecklist()/n")

        # Get biosecID from AJAX url param
        bioID = biosecID

        # Get checkArr from AJAX data param
        chArr = []
        chArr = request.POST.getlist("checkArr[]")

        if bioID is None:
            # (ERROR) Invalid or null biosecID
            debug("(ERROR) Invalid or null biosecID")
            return JsonResponse({"error": "Invalid biosecurity ID."}, status=400)

        else:
            debug("in update_bioChecklist() -- bioID: " + str(bioID)) 

            # For checking if Biocheck array is complete
            isComplete = True

            for index, value in enumerate(chArr): 
                if value is None:
                    # (ERROR) Incomplete checklist array inputs
                    isComplete = False
                    debug("(ERROR) Incomplete checklist array inputs")
                    return JsonResponse({"error": "Incomplete Biosecurity checklist inputs."}, status=400)

                else:
                    # convert str element to int
                    int(value)
                    print(list((index, value)))

            if isComplete:
                extBio = ExternalBiosec.objects.get(pk=bioID)
                intBio = InternalBiosec.objects.get(pk=bioID)

                if extBio is not None and intBio is not None:

                    # Check if bioChecklist is w/in a day
                    extDateDiff = datetime.now(timezone.utc) - extBio.last_updated
                    intDateDiff = datetime.now(timezone.utc) - intBio.last_updated
                    
                    # debug("extDateDiff.days" + str(extDateDiff.days))
                    # debug("intDateDiff" + str(intDateDiff.days))

                    if extDateDiff.days > 1 or intDateDiff.days > 1:
                        # Get biosec fields from not updated record in db
                        bioDict = {
                            # External bio
                            'prvdd_foot_dip'        : extBio.prvdd_foot_dip,  
                            'prvdd_alco_soap'       : extBio.prvdd_alco_soap,     
                            'obs_no_visitors'       : extBio.obs_no_visitors,     
                            'prsnl_dip_footwear'    : extBio.prsnl_dip_footwear,  
                            'prsnl_sanit_hands'     : extBio.prsnl_sanit_hands,   
                            'chg_disinfect_daily'   : extBio.chg_disinfect_daily,

                            # Internal bio
                            'disinfect_prem'        : intBio.disinfect_prem,
                            'disinfect_vet_supp'    : intBio.disinfect_vet_supp,   
                        }
                        # Serialize dictionary
                        jsonStr = json.dumps(bioDict)
                        
                        # # (SUCCESS) Biochecklist updated. Send to client side (js)
                        # return JsonResponse({"instance": jsonStr}, status=200)

                        debug("(ERROR) Cannot edit. int-ext Biosec exceeds 1 day.")

                        return JsonResponse({"instance": jsonStr, "error": "Cannot edit Biosecurity Checklist because it exceeds 1 day."}, status=400)
                    else:
                        # External Biosec
                        extBio.prvdd_foot_dip       = chArr[0]
                        extBio.prvdd_alco_soap      = chArr[1]
                        extBio.obs_no_visitors      = chArr[2]
                        extBio.prsnl_dip_footwear   = chArr[3]
                        extBio.prsnl_sanit_hands    = chArr[4]
                        extBio.chg_disinfect_daily  = chArr[5]
                        
                        # Internal Biosec
                        intBio.disinfect_prem       = chArr[6]
                        intBio.disinfect_vet_supp   = chArr[7]

                        # Save both biosec fields in db
                        extBio.save()
                        intBio.save()

                        # Get updated biosec fields; then format biosec fields in a dict
                        bioDict = {
                            # External bio
                            'prvdd_foot_dip'        : extBio.prvdd_foot_dip,  
                            'prvdd_alco_soap'       : extBio.prvdd_alco_soap,     
                            'obs_no_visitors'       : extBio.obs_no_visitors,     
                            'prsnl_dip_footwear'    : extBio.prsnl_dip_footwear,  
                            'prsnl_sanit_hands'     : extBio.prsnl_sanit_hands,   
                            'chg_disinfect_daily'   : extBio.chg_disinfect_daily,

                            # Internal bio
                            'disinfect_prem'        : intBio.disinfect_prem,
                            'disinfect_vet_supp'    : intBio.disinfect_vet_supp,   
                        }

                        # Serialize dictionary
                        jsonStr = json.dumps(bioDict)
                        
                        # (SUCCESS) Biochecklist updated. Send to client side (js)
                        return JsonResponse({"instance": jsonStr, "status_code":"200"}, status=200)

                else:
                    # (ERROR) Biosecurity record not found in db.
                    debug("(ERROR) Biosecurity record not found.")
                    return JsonResponse({"error": "Biosecurity record not found."}, status=400)   
            else:
                # (ERROR) Incomplete checklist array inputs
                debug("(ERROR) Incomplete checklist array inputs")
                return JsonResponse({"error": "Incomplete Biosecurity checklist inputs."}, status=400)

    return JsonResponse({"error": "not an AJAX post request"}, status=400)

# (POST) For adding a Biosec Checklist
def post_addChecklist(request, farmID):
    # print("TEST LOG: in post_addChecklist/n")

    if request.method == "POST":
        
        # Get farmID from URL param and check if farmID exists
        if Farm.objects.filter(id=farmID).exists():
            farmID = farmID

            debug("in POST biochecklist /n: farmID -- " + str(farmID))
            
            # If none selected in btn group, default value taken from btn tag is None
            biosecArr = [
                request.POST.get("disinfect_prem", None),
                request.POST.get("prvdd_foot_dip", None),
                request.POST.get("prvdd_alco_soap", None),
                request.POST.get("obs_no_visitors", None),
                request.POST.get("disinfect_vet_supp", None),
                request.POST.get("prsnl_dip_footwear", None),
                request.POST.get("prsnl_sanit_hands", None),
                request.POST.get("cng_disinfect_daily", None),
            ]
            
            checkComplete = True # bool for checking if checklist is complete

            # Array length must be 8 for the 8 fields in a Biosec checklist.
            print("biosecArr len(): " + str(len(biosecArr)))

            # debug("TEST LOG: List of Biocheck values")
            for index, value in enumerate(biosecArr): 
                if value is None:
                    # (ERROR) Incomplete input/s for Biosecurity Checklist
                    # debug("ERROR: Index value in biosec is None.")
                    checkComplete = False

                    messages.error(request, "Incomplete input/s for Biosecurity Checklist.", extra_tags='add-checklist')
                    return redirect('/add-checklist/' + farmID)


            if checkComplete: # (SUCCESS) Checklist input complete, proceed to add in db

                # Get current biosec Measures from Farm
                bioMeasure = Farm.objects.filter(id=farmID).select_related("intbio", "extbio").annotate(
                                waste_mgt   = F("intbio__waste_mgt"),
                                isol_pen    = F("intbio__isol_pen"),
                                foot_dip    = F("intbio__foot_dip"),
                                bird_proof  = F("extbio__bird_proof"),
                                perim_fence = F("extbio__perim_fence"),
                                fiveh_m_dist = F("extbio__fiveh_m_dist")
                ).values(
                    "waste_mgt",
                    "isol_pen",
                    "bird_proof",
                    "perim_fence",
                    "foot_dip",
                    "fiveh_m_dist"
                ).first()

                # debug("BIOMEASURE: -- " + str(bioMeasure))

                # init Biosec and Farm models
                extBio = ExternalBiosec() 
                intBio = InternalBiosec() 
                farmQuery = Farm.objects.get(pk=farmID)

                # Put bioMeasures into External model
                extBio.bird_proof   = bioMeasure.get("bird_proof")
                extBio.perim_fence  = bioMeasure.get("perim_fence")
                extBio.fiveh_m_dist = bioMeasure.get("fiveh_m_dist")

                # Put bioMeasures into Internal model
                intBio.waste_mgt    = bioMeasure.get("waste_mgt")
                intBio.isol_pen     = bioMeasure.get("isol_pen")
                intBio.foot_dip     = bioMeasure.get("foot_dip")

                # Put biochecklist attributes into External model
                extBio.ref_farm = farmQuery
                extBio.prvdd_foot_dip       = biosecArr[1]
                extBio.prvdd_alco_soap      = biosecArr[2]
                extBio.obs_no_visitors      = biosecArr[3]
                extBio.prsnl_dip_footwear   = biosecArr[5]
                extBio.prsnl_sanit_hands    = biosecArr[6]
                extBio.chg_disinfect_daily  = biosecArr[7]
                
                # Put biochecklist attributes into Internal model
                intBio.ref_farm = farmQuery
                intBio.disinfect_prem      = biosecArr[0]
                intBio.disinfect_vet_supp  = biosecArr[4]

                # Update data of the INTERNAL, EXTERNAL Biosec tables
                extBio.save()
                intBio.save()

                # Update biosec FKs in Farm model
                farm = Farm.objects.filter(id=farmID).select_related("intbio", "extbio").first()
                farm.intbio = intBio
                farm.extbio = extBio

                farm.save()

                # Format time to be passed on message.success
                ts = extBio.last_updated 
                df = ts.strftime("%m/%d/%Y")
                # debug(extBio.last_updated)
                
                # (SUCCESS) Biochecklist has been added. Properly redirect to Biosec main page
                messages.success(request, "Checklist dated " + df + " has been successfully added.", extra_tags='add-checklist')
                return redirect('/biosecurity/' + farmID)
        
            else:
                # (ERROR) Incomplete input/s for Biosecurity Checklist
                debug("ERROR: Incomplete input/s for Biosecurity Checklist.")
                messages.error(request, "Incomplete input/s for Biosecurity Checklist.", extra_tags='add-checklist')
                return redirect('/add-checklist/' + farmID)
        else:
            # (ERROR) Invalid farmID
            debug("ERROR: Invalid/None-type farmID from parameter.")
            messages.error(request, "Farm record not found.", extra_tags='add-checklist')
            return redirect('/biosecurity')

    else:
        # (ERROR) not an AJAX Post request
        messages.error(request, "Incomplete input/s for Biosecurity Checklist.", extra_tags='add-checklist')
        return redirect('/add-checklist/' + farmID)

# (POST-AJAX) For deleting a Biosec Checklist based on biosecID and farmID
def delete_bioChecklist(request, biosecID, farmID):
    """
    (POST-AJAX) For deleting a biosecurity checklist based on biosecID and farmID from dropdowns.
        Handles two scenarios:
        - (1) To be deleted Checklist is current Biosec in Farm
        - (2) Not current checklist in Farm, simply delete record
    """

    if request.method == 'POST':

        # print("TEST LOG: in delete_bioChecklist()/n")

        # Get biosecID from AJAX url param
        bioID = biosecID

        if bioID is None:
            # (ERROR) Invalid or null biosecID
            debug("(ERROR) Invalid or null biosecID")
            return JsonResponse({"error": "Invalid biosecurity ID."}, status=400)

        else:
            
            debug("in delete_bioChecklist() -- bioID: " + str(bioID)) 

            # check if to be deleted Checklist is current int-extbio in Farm
            currFarm = Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').first()
            intBio = currFarm.intbio
            extBio = currFarm.extbio

            debug("intBio.id -- " + str(intBio.id))
            debug("extBio.id -- " + str(extBio.id))


            if str(intBio.id) == str(bioID) and str(extBio.id) == str(bioID):
                # (CASE 1) To be deleted Checklist is current Biosec in Farm
                ExternalBiosec.objects.filter(id=bioID).delete()
                InternalBiosec.objects.filter(id=bioID).delete()

                # get 2nd latest biosec after deletion
                lateExt = ExternalBiosec.objects.filter(ref_farm_id=farmID).only(
                    'last_updated',
                ).order_by('-last_updated').first()

                lateInt = InternalBiosec.objects.filter(ref_farm_id=farmID).only(
                    'last_updated',
                ).order_by('-last_updated').first()

                debug("lateInt.id -- " + str(lateInt.id))
                debug("lateExt.id -- " + str(lateExt.id))

                # replace biosec FKs in Farm
                farm = Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').first()

                farm.intbio = lateInt
                farm.extbio = lateExt
                farm.save()

                debug("save() farm.intbio -- " + str(farm.intbio.id))
                debug("save() farm.extbio -- " + str(farm.extbio.id))

            else:
                # (CASE 2) Not current checklist in Farm, simply delete record
                ExternalBiosec.objects.filter(id=bioID).delete()
                InternalBiosec.objects.filter(id=bioID).delete()


            # (SUCCESS) Biosec record has been deleted.
            return JsonResponse({"success": "Biosecurity record has been deleted.", "status_code":"200"}, status=200)

    return JsonResponse({"error": "not an AJAX post request"}, status=400)

def biosec_view(request):
    """
    For getting all Biosecurity details under a Farm. 
    This function gets the ID of the first Farm due to no passed farmID as parameter.

    - (1) farms under Technician user
    """

    # print("TEST LOG: in Biosec view/n")

    # (1) Get all Farms under the logged-in technician User
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all().order_by('id')

    # array to store all farms under each area
    techFarmsList = []

    for area in areaQry :
        # collect the corresponding hog raiser details for each farm 
        techFarmQry  = Farm.objects.filter(area_id=area.id).values("id").order_by('id').all()

        # pass all data into an array
        for farm in techFarmQry:
            farmObject = {
                "id": farm["id"],
            }
            techFarmsList.append(farmObject)

    # debug("techFarmsList -- " + str(techFarmsList))
    
    return render(request, 'farmstemp/biosecurity.html', {'farmID' : 0, 'farmList': techFarmsList}) 

# For getting all Biosec checklist versions under a Farm based on farmID.
def select_biosec(request, farmID):
    """
    For getting all Biosecurity details under a Farm. 
    This serves as a search function when a farmID or farm code is selected from its dropdown.

    - (1) farms under Technician user, 
    - (2) latest intbio-extbio Checklist, 
    - (3) all biosec IDs and dates within that Farm, 
    - (4) approved activities
    """

    # # (1) Get all Farms under the logged-in technician User
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all().order_by('id')

    # array to store all farms under each area
    techFarmsList = []

    for area in areaQry :
        # print(str(area.id) + str(area.area_name))

        # collect the corresponding hog raiser details for each farm 
        techFarmQry  = Farm.objects.filter(area_id=area.id).values(
            "id"
        ).order_by('id').all()

        # pass all data into an array
        for farm in techFarmQry:
            farmObject = {
                "id": farm["id"],
            }
            techFarmsList.append(farmObject)
        
    # debug("techFarmsList -- " + str(techFarmsList))

    # (ERROR) for checking technician Areas that have no Farms and null farmID
    if not techFarmsList or farmID is None: 
        messages.error(request, "Farm record/s not found.", extra_tags="view-biosec")
        return render(request, 'farmstemp/biosecurity.html', {})
    else:
        # Select Biochecklist with latest date
        currbioQuery = Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').all()
        

        # (2) Get latest instance of Biochecklist
        currbioObj = currbioQuery.first()
        # print("TEST LOG biosec_view(): Queryset currbio-- " + str(currbioQuery.query))


        # (3) Get all biosecID, last_updated in extbio under a Farm
        extQuery = ExternalBiosec.objects.filter(ref_farm_id=farmID).only(
            'last_updated',
        ).order_by('-last_updated')


        # (ERROR) for checking Farms that have no Biosec records
        if not extQuery.exists() or currbioObj.intbio is None or currbioObj.extbio is None: 
            messages.error(request, "No biosecurity records for this farm.", extra_tags="view-biosec")
            return render(request, 'farmstemp/biosecurity.html', {'farmID' : farmID, 'farmList': techFarmsList})

        # (4) GET ACTIVITIES
        actQuery = Activity.objects.filter(ref_farm_id=farmID).filter(is_approved=True).all().order_by('-date')

        actList = []

        # store all data to an array
        for activity in actQuery:
            
            actList.append({
                'id' : activity.id,
                'date' : activity.date,
                'format_date' : (activity.date).strftime('%Y-%m-%d'),
                'trip_type' : activity.trip_type,
                'time_arrival' : activity.time_arrival,
                'format_arrival' : (activity.time_arrival).strftime('%H:%M:%S'),
                'time_departure' : activity.time_departure,
                'format_departure' : (activity.time_departure).strftime('%H:%M:%S'),
                'num_pigs_inv' : activity.num_pigs_inv,
                'remarks' : activity.remarks,
            })

        # pass in context:
        # - (1) farmIDs under Technician user, 
        # - (2) latest intbio-extbio Checklist, 
        # - (3) all biocheck IDs and dates within that Farm, 
        # - (4) approved activities
        return render(request, 'farmstemp/biosecurity.html', {'farmID' : int(farmID), 'farmList': techFarmsList, 'currBio': currbioObj, 'bioList': extQuery, 'activity' : actList}) 

    return render(request, 'farmstemp/biosecurity.html', {}) 

def addChecklist_view(request, farmID):
    """
    For passing farmID from Biosecurity page to addChecklist page ("add-checklist.html")
    """
    # debug("TEST LOG: in addChecklist_view/n")

    return render(request, 'farmstemp/add-checklist.html', { 'farmID' : int(farmID) })

def techAssignment(request):
    areasData = []
    areas = Area.objects.select_related("tech_id").annotate(
        curr_tech = Concat('tech_id__first_name', Value(' '), 'tech_id__last_name')
    ).order_by('area_name').values()
    techs = User.objects.filter(groups__name="Field Technician").annotate(
        name = Concat('first_name', Value(' '), 'last_name'),
    ).values(
        "id",
        "name",
    )

    for a in areas:
        # get total pigs per area
        aFarmQry = Farm.objects.filter(area=a["id"]).all()
        total_pigs = 0
        for af in aFarmQry:
            total_pigs += af.total_pigs

        areaObject = {
            "id": str(a["id"]),
            "area_name": a["area_name"],
            "curr_tech_id": a["tech_id"],
            "curr_tech": a["curr_tech"],
            "farm_count": Farm.objects.filter(area=a["id"]).count(),
            "total_pigs": total_pigs
        }
        areasData.append(areaObject)
    context = {
        "areasData":areasData,
        "technicians":techs
    }
    return render(request, 'farmstemp/assignment.html', context)

def search_techTasks(request, techID):
    """
    For retrieving details of tasks left by a technician which includes:
    - (1) technician name
    - (2) Farm Biosecurity details
    - (3) Incident records (Active and Pending)
    - (4) Recent member announcements created
    """

    # debug("in search_techTasks()/n")
    # debug("techID: " + techID)

    # (1) Get formatted technician name
    tech = User.objects.filter(groups__name="Field Technician").filter(id=int(techID)).annotate(
        full_name = Concat('first_name', Value(' '), 'last_name'),
        ).values(
        "full_name"
        ).first()

    techName = " "
    if tech is None:
        debug("ERROR: Technician not found.")
        messages.error(request, "Technician not found.", extra_tags='search-techTasks')
        return render(request, 'farmstemp/assignment.html', {})
    else:
        techName = tech["full_name"]

    # (2) Get Farm details 
    farmQry = Farm.objects.filter(area__tech_id=int(techID)).select_related('extbio').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        a_name=F("area__area_name"),
        last_update = F("extbio__last_updated")
        ).values(
            "id",
            "fname",
            "lname", 
            "a_name",
            "total_pigs",
            "last_update"
            ).order_by("id").all()

    farmsData = []
    for f in farmQry:
        farmObject = {
            "code":  f["id"],
            "area_name": f["a_name"],
            "raiser": " ".join((f["fname"],f["lname"])),
            "num_pigs": str(f["total_pigs"]),
            "last_inspected": f["last_update"]
        }
        farmsData.append(farmObject)

    # (3) Get Incident details
    incidData = []
    for farm in farmQry:
        # for current Pigpen version
        latestPigpen = Pigpen_Group.objects.filter(ref_farm_id=farm["id"]).order_by("-date_added").first()

        # (1.1) Incidents Reported (code, date_filed, num_pigs_affected, report_status)
        incidentQry = Hog_Symptoms.objects.filter(ref_farm__area__tech_id=int(techID)).filter(pigpen_grp_id=latestPigpen.id).filter(~Q(report_status='Resolved')).only(
            'date_filed',
            'date_updated', 
            'report_status',
            'num_pigs_affected').order_by("-date_filed").all()

        # (1.2) Incidents Reported (symptoms list)
        symptomsList = Hog_Symptoms.objects.filter(ref_farm__area__tech_id=int(techID)).filter(pigpen_grp_id=latestPigpen.id).filter(~Q(report_status='Resolved')).values(
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
        
        incidObject = {
            "farm_code":  farm["id"],
            "area_name": f["a_name"],
            "incident_symptomsList": zip(incidentQry, symptomsList)
        }
        incidData.append(incidObject)

    # (4) Get Mem Announcements
    memQry = Mem_Announcement.objects.filter(author_id=int(techID)).filter(is_approved=True).order_by("-timestamp")    

    debug(techName)

    return render(request, 'farmstemp/assignment.html', {"techName": techName, "farmBioList": farmsData,
                                                                                "incidList":  incidData,
                                                                                "announceList": memQry})


def assign_technician(request):
    """
    Assign technician to area through ajax
    """

    areaQry = request.POST.get("area")
    techQry = request.POST.get("technician")

    # validate if input will be valid
    ## check if area exists
    ## check if technician exists
    area = Area.objects.filter(area_name=areaQry)
    technician = User.objects.filter(id=techQry)
    if(area.exists() and technician.exists()):
        # save changes
        a = area.get()
        a.tech_id = technician.get()
        a.save()
        # return output
        return HttpResponse("Technician assigned",status=200)
    # else abort
    # return output
    return HttpResponse("Area or Technician Not Found",status=404)
    
def save_area(request):
    """
    Create a new area, abort if area with same string is found
    """

    areaName = request.POST.get("area")
    is_exist = Area.objects.filter(area_name = areaName).exists()
    if(not is_exist):
        Area(area_name = areaName, tech_id = None).save()
        return HttpResponse("Save success")
    return HttpResponse("Save Fail", status=400)
    

def formsApproval(request):
    """
    - Redirect to Forms Approval Page
    - For Module 1, display all activity forms with corresponding status acc. to user
    - For Module 2, display all mortality forms with correspinding status acc. to user
    """

    ## ACTIVITY FORMS
    # get all activity forms
    actQuery = Activities_Form.objects.filter(is_latest=True).order_by("-date_added")
    # print(actQuery)

    activityList = []

    for act in actQuery:       
        getTech = User.objects.filter(id=act.act_tech_id).annotate(
            name = Concat('first_name', Value(' '), 'last_name'),
        ).values("name").first()

        if act.is_checked == True:
            status = 'Approved'
        elif act.is_checked == False:
            status = 'Rejected'
        elif act.is_checked == None:
            status = 'Pending'

        # pass into object and append to list 
        if request.user.groups.all()[0].name == "Field Technician" :
            if act.act_tech_id == request.user.id:
                activityObject = {
                        "id" : act.id,
                        "date_added" : act.date_added,
                        "code" : act.code,
                        "status" : status,
                        "prepared_by" : str(request.user.first_name) + " " + str(request.user.last_name),
                        "farmID" : int(act.ref_farm_id) }

                activityList.append(activityObject)
                
        else:
            activityObject = {
                "id" : act.id,
                "date_added" : act.date_added,
                "code" : act.code,
                "status" : status,
                "prepared_by" : getTech["name"],
                "farmID" : int(act.ref_farm_id) }
    
            activityList.append(activityObject)


    return render(request, 'farmstemp/forms-approval.html', { 'actList' : activityList })

def selectedActivityForm(request, activityFormID, activityDate):
    """
    - Display all activity rows for the selected activity form

    activityFormID = id value of selected activity form
    activityDate = date_added value of activity form selected
    """

    # get details of activity form
    actFormQuery = Activities_Form.objects.filter(id=activityFormID).first()

    # get latest
    latestForm = Activities_Form.objects.filter(code=actFormQuery.code).last()

    # set status of activity form
    if actFormQuery.is_checked == True :
        status = 'Approved'
    elif actFormQuery.is_checked == False :
        status = 'Rejected'
    elif actFormQuery.is_checked == None :
        status = 'Pending'

    # get all activities under activity form
    actQuery = Activity.objects.filter(activity_form_id=activityFormID).all().order_by("id")
    actList = []

    # store all data to an array
    for activity in actQuery:
        actList.append({
            'id' : activity.id,
            'date' : activity.date,
            'format_date' : (activity.date).strftime('%Y-%m-%d'),
            'trip_type' : activity.trip_type,
            'time_arrival' : activity.time_arrival,
            'format_arrival' : (activity.time_arrival).strftime('%H:%M:%S'),
            'time_departure' : activity.time_departure,
            'format_departure' : (activity.time_departure).strftime('%H:%M:%S'),
            'num_pigs_inv' : activity.num_pigs_inv,
            'remarks' : activity.remarks
        })

    # get all other versions of selected activity form
    versionList = Activities_Form.objects.filter(code=actFormQuery.code).all().order_by("-id")
    
    # get reference data (farm)
    techFarmQry = Farm.objects.filter(id=actFormQuery.ref_farm_id).select_related('hog_raiser', 'area').annotate(
                    raiser      = Concat('hog_raiser__fname', Value(' '), 'hog_raiser__lname'),
                    contact     = F("hog_raiser__contact_no"),
                    farm_area   = F("area__area_name"))

    farmRef = techFarmQry.values(
        "id",
        "raiser",
        "contact",
        "directly_manage",
        "farm_address",
        "farm_area",
        "roof_height",
        "wh_length", 
        "wh_width",
        "total_pigs",
        "feed_trough",
        "bldg_cap",
        "medic_tank",
        "bldg_curtain",
        "road_access",
    ).first()

    # get reference data (health)
    start_weight = 0.0
    end_weight   = 0.0

    end_subtotal = 0.0
    pigs_sold = 0

    # get latest version of Pigpen
    latestPP = Pigpen_Group.objects.filter(ref_farm_id=actFormQuery.ref_farm_id).order_by("-date_added").first()
    pigpenQry = Pigpen_Row.objects.filter(pigpen_grp_id=latestPP.id).order_by("id")
    
    # get current starter and fattener weights acc. to current Pigpen
    s_weightQry = Farm_Weight.objects.filter(pigpen_grp_id=latestPP.id).filter(is_starter=True).first()
    e_weightQry = Farm_Weight.objects.filter(pigpen_grp_id=latestPP.id).filter(is_starter=False).all()

    # assign values for start and end weight
    if s_weightQry is not None:
        start_weight = s_weightQry.ave_weight

    if len(e_weightQry):
        for e in e_weightQry:
            end_subtotal += e.total_kls
            pigs_sold += e.total_numHeads

        end_weight = round(end_subtotal/pigs_sold, 2)

    # compute for mortality rate (borrowed from comp_MortRate function)
    total_pigs = 0
    for pen in pigpenQry:
        total_pigs += pen.num_heads

    # Get latest Mortality record of the Farm (w Pigpen filter)
    mortQry = Mortality.objects.filter(ref_farm_id=actFormQuery.ref_farm_id).filter(mortality_form__pigpen_grp_id=latestPP.id).order_by('-mortality_date')

    mortality_rate = 0
    toDate = 0

    if mortQry is not None:
        for m in mortQry:
            toDate += m.num_today

        mortality_rate = (toDate / total_pigs) * 100

    # count total number of cases reported
    total_incidents = Hog_Symptoms.objects.filter(ref_farm_id=actFormQuery.ref_farm_id).filter(pigpen_grp_id=latestPP.id).count()

    # count total number of active cases
    total_active = Hog_Symptoms.objects.filter(ref_farm_id=actFormQuery.ref_farm_id).filter(pigpen_grp_id=latestPP.id).filter(report_status="Active").count()

    healthRef = {
        "ave_startWeight":  start_weight,
        "ave_endWeight":    end_weight,
        "mortality_rate":   round(mortality_rate, 2),
        "total_incidents":  total_incidents,
        "total_active":     total_active,
    }

    return render(request, 'farmstemp/selected-activity-form.html', {'activityForm' : ActivityForm(), 'activities' : actList, 'latest' : latestForm, 'healthRef' : healthRef,
                                                                    'formStatus' : status, 'actForm' : actFormQuery, 'actFormList' : versionList, 'farmRef' : farmRef})

def approveActivityForm(request, activityFormID):
    """
    - Modify is_checked value of selected activity form
    - Update last_updated and date_approved

    activityFormID = id value of activity form selected
    """

    activity_form = Activities_Form.objects.filter(id=activityFormID).first()
    # print(str(activity_form))

    # get today's date
    dateToday = datetime.now(timezone.utc)

    if request.method == 'POST':
        # update activity form fields for user approvals
        # is_checked for live op
        if request.POST.get("is_checked") == 'true' :
            activity_form.is_checked = True

            if request.user.groups.all()[0].name == "Livestock Operation Specialist":
                activity_form.act_liveop_id = request.user.id
        
        activity_form.save()

        # get all activities under activity form
        actQuery = Activity.objects.filter(activity_form_id=activityFormID).all()
        for activity in actQuery:
            activity.last_updated = dateToday
            
            if activity_form.is_checked == True :
                activity.is_approved = True
                activity.date_approved = dateToday

            activity.save()
    

        messages.success(request, "Activity Form has been approved by " + str(request.user.groups.all()[0].name) + ".", extra_tags='update-activity')
        return JsonResponse({"success": "Activity Form has been approved by " + str(request.user.groups.all()[0].name) + "."}, status=200)

    messages.error(request, "Failed to approve activities.", extra_tags='update-activity')
    return JsonResponse({"error": "Not a POST method"}, status=400)

def rejectActivityForm(request, activityFormID):
    """
    - Modify is_checked value of selected activity form
    - Update last_updated

    activityFormID = id value of activity form selected
    """

    activity_form = Activities_Form.objects.filter(id=activityFormID).first()
    # print(str(activity_form))

    # get today's date
    dateToday = datetime.now(timezone.utc)

    if request.method == 'POST':
        # print(request.POST)

        # update activity form fields for user approvals
        # is_checked for live op
        if request.POST.get("is_checked") == 'false' :
            activity_form.is_latest = False
            activity_form.is_checked = False
            activity_form.reject_reason = request.POST.get("reason")

            if request.user.groups.all()[0].name == "Livestock Operation Specialist":
                activity_form.act_liveop_id = request.user.id

        activity_form.save()

        # duplicate instance (for a new version)
        activity_form.pk = None
        activity_form.is_latest = True
        activity_form.save()

        # get all activities under activity form
        actQuery = Activity.objects.filter(activity_form_id=activityFormID).all()
        for activity in actQuery:
            activity.last_updated = dateToday
            
            if activity_form.is_checked == False :
                activity.is_approved = False

            activity.save()

            # duplicate instance (for a new version)
            activity.pk = None
            activity.activity_form = activity_form
            activity.save()

        messages.success(request, "Activity Form has been rejected by " + str(request.user.groups.all()[0].name) + ".", extra_tags='update-activity')
        return JsonResponse({"success": "Activity Form has been approved by " + str(request.user.groups.all()[0].name) + "."}, status=200)

    messages.error(request, "Failed to reject activities.", extra_tags='update-activity')
    return JsonResponse({"error": "Not a POST method"}, status=400)

def resubmitActivityForm(request, activityFormID, farmID, activityDate):
    """
    - Resubmit rejected activity form and modify approval status
    - Add new activities to database and connect to activity form (as FK)
    - Save details to activity and add FK of current farm table
    """
    
    # get ID of current technician
    techID = request.user.id

    # get activity form from ID
    activity_form = Activities_Form.objects.filter(id=activityFormID).first()

    # get today's date
    dateToday = datetime.now(timezone.utc)

    if request.method == 'POST':
        # debug(request.POST)
        numActivities = int(len(request.POST)/6)

        # pass all values into each of the array activityList
        activityList = []

        i = 0
        while i < numActivities:
            actDate = str('activityList[') + str(i) + str('][date]')
            actType = str('activityList[') + str(i) + str('][trip_type]')
            actArrival = str('activityList[') + str(i) + str('][time_arrival]')
            actDeparture = str('activityList[') + str(i) + str('][time_departure]')
            actNumPigsInv = str('activityList[') + str(i) + str('][num_pigs_inv]')
            actRemarks = str('activityList[') + str(i) + str('][remarks]')

            if request.POST.get(actNumPigsInv, default=None) == '':
                num_pigs_inv = 0
            else :
                num_pigs_inv =  request.POST.get(actNumPigsInv, default=None)

            activityObject = {
                "date" : request.POST.get(actDate, default=None),
                "trip_type" : request.POST.get(actType, default=None),
                "time_arrival" : request.POST.get(actArrival, default=None),
                "time_departure" : request.POST.get(actDeparture, default=None),
                "num_pigs_inv" : num_pigs_inv,
                "remarks" : request.POST.get(actRemarks, default=None),
            }

            activityList.append(activityObject)
            i += 1
        
        # print("TEST LOG activityList: " + str(activityList))

        # reset approval status of activity form
        activity_form.reject_reason = None
        activity_form.is_checked = None
        activity_form.date_added = datetime.now(timezone.utc)

        activity_form.save()
        
        # pass all activityList objects into Activity model
        x = 0

        for act in activityList:
            act = activityList[x]

            # create new instance of Activity model
            activity = Activity.objects.create(
                ref_farm_id = farmID,
                date = act['date'],
                trip_type = act['trip_type'],
                time_arrival = act['time_arrival'],
                time_departure = act['time_departure'],
                num_pigs_inv = act['num_pigs_inv'],
                remarks = act['remarks'],
                activity_form_id = activity_form.id
            )

            activity.save()
            x += 1
        
        messages.success(request, "Activity Form has been resubmitted.", extra_tags='update-activity')
        return JsonResponse({"success": "Activity Form has been resubmitted."}, status=200)

    messages.error(request, "Failed to resubmit Activity Form.", extra_tags='update-activity')
    return JsonResponse({"error": "Not a POST method"}, status=400)

def addActivity(request, farmID):
    """
    - Redirect to Add Activity Page and render corresponding Django form
    - Add new activity to database and connect to new instance of Activity Form (as FK)
    - Save details to activity and add FK of current farm table
    - Django forms will first check the validity of input (based on the fields within models.py)

    farmID - selected farmID passed as parameter
    """
    
    # generate code number
    latestForm = Activities_Form.objects.order_by("-code").first()
    try:
        code = int(latestForm.code) + 1
    except:
        code = 1
    
    # collected farmID of selected tech farm
    farmQuery = Farm.objects.get(pk=farmID)
    
    if request.method == 'POST':
        # print("TEST LOG: Add Activity has POST method") 
        # debug(request.POST)

        activityForm = ActivityForm(request.POST)

        # pass all values into one record in activityList
        activityList = []

        i = 0
        for date in request.POST.getlist('date', default=None):
            if request.POST.getlist('num_pigs_inv', default=None)[i] == '' :
                num_pigs_inv = 0
            else :
                num_pigs_inv = request.POST.getlist('num_pigs_inv', default=None)[i]

            activityObject = {
                "date" : request.POST.getlist('date', default=None)[i],
                "trip_type" : request.POST.getlist('trip_type', default=None)[i],
                "time_arrival" : request.POST.getlist('time_arrival', default=None)[i],
                "time_departure" : request.POST.getlist('time_departure', default=None)[i],
                "num_pigs_inv" : num_pigs_inv,
                "remarks" : request.POST.getlist('remarks', default=None)[i],
            }
            
            activityList.append(activityObject)
            i += 1

        # debug(activityList)
        
        if activityForm.is_valid():

            # create instance of Activity Form model
            activity_form = Activities_Form.objects.create(
                code = code,
                is_latest = True,
                date_added = datetime.now(timezone.utc),
                act_tech_id = request.user.id,
                ref_farm = farmQuery,
            )
            activity_form.save()

            # pass all activityList objects into Activity model
            x = 0
            for act in activityList:
                act = activityList[x]

                # create new instance of Activity model
                activity = Activity.objects.create(
                    ref_farm = farmQuery,
                    date = act['date'],
                    trip_type = act['trip_type'],
                    time_arrival = act['time_arrival'],
                    time_departure = act['time_departure'],
                    num_pigs_inv = act['num_pigs_inv'],
                    remarks = act['remarks'],
                    activity_form_id = activity_form.id
                )

                activity.save()
                x += 1

            # update last_updated of farm
            farmQuery.last_updated = datetime.now(timezone.utc)
            farmQuery.save()
            
            messages.success(request, "Activity Form has been sent for approval.", extra_tags='add-activity')
            return redirect('/biosecurity/' + str(farmID))
            
        else:
            # print("TEST LOG: activityForm is not valid")
            formError = str(activityForm.non_field_errors().as_text)

            messages.error(request, "Error adding activity. " + str(re.split("\'.*?",formError)[1]), extra_tags='add-activity')

    else:
        print("TEST LOG: Add Activity is not a POST method")

        # if form has no input yet, only display an empty form
        activityForm = ActivityForm()

    # pass django form and farmID to template
    return render(request, 'farmstemp/add-activity.html', { 'activityForm' : activityForm, 'farmID' : int(farmID), 'code' : code })

def saveActivity(request, farmID, activityID):
    """
    - Update selected activity under current farm
    - Collect data from backend-scripts.js
    
    activityID - selected activityID passed as parameter
    farmID - selected farmID passed as parameter
    """

    # for setting Date input filters to today's date
    dateToday = datetime.now(timezone.utc)

    if request.method == 'POST':
        # print("TEST LOG: Edit Activity is a POST Method")
        
        # collect data from inputs
        date = request.POST.get("date")
        trip_type = request.POST.get("trip_type")
        time_departure = request.POST.get("time_departure")
        time_arrival = request.POST.get("time_arrival")
        num_pigs_inv = request.POST.get("num_pigs_inv")
        remarks = request.POST.get("remarks")
        # print("DATA COLLECTED: " + str(date) + " - " + str(trip_type) + " - " + str(time_arrival) + " to " + str(time_departure) )

        # get activity to be updated
        activity = Activity.objects.filter(id=activityID).first()
        # print("OLD ACTIVITY: " + str(activity.date) + " - " + str(activity.trip_type) + " - " + str(activity.time_arrival) + " to " + str(activity.time_departure) )

        # assign new values
        activity.date = date
        activity.trip_type = trip_type
        activity.time_departure = time_departure
        activity.time_arrival = time_arrival
        activity.num_pigs_inv = num_pigs_inv
        activity.remarks = remarks
        activity.last_updated = dateToday
        
        activity.save()
        # print("UPDATED ACTIVITY: " + str(activity.date) + " - " + str(activity.trip_type) + " - " + str(activity.time_arrival) + " to " + str(activity.time_departure) )
        messages.success(request, "Activity has been updated.", extra_tags='update-activity')

        return JsonResponse({"success": "Activity has been updated."}, status=200)

    return JsonResponse({"error": "Not a POST method"}, status=400)

def deleteActivity(request, activityID):
    """
    - Delete selected activity under current farm
    
    activityID - selected activityID passed as parameter
    """
    
    if request.method == 'POST':
        # print("TEST LOG: Delete Activity is a POST Method")
    
        Activity.objects.filter(id=activityID).delete()
        messages.success(request, "Activity has been deleted.", extra_tags='update-activity')
        return JsonResponse({"success": "Activity has been deleted."}, status=200)

    return JsonResponse({"error": "Not a POST method"}, status=400)

def memAnnouncements(request):
    """
    Display approved and unapproved announcements
    """
    
    announcements = Mem_Announcement.objects.select_related("author").annotate(
        name = Concat('author__first_name', Value(' '), 'author__last_name')
    ).values(
        "id",
        "timestamp",
        "title",
        "category",
        "recip_area",
        "name",
        "reject_reason"
    ).order_by("-timestamp")

    if request.user.groups.all()[0].name == "Assistant Manager":
        context = {
            "approved": announcements.filter(is_approved = True),
            "rejected": announcements.filter(is_approved = False),
            "unapproved": announcements.filter(is_approved = None),
        }
    else:
        context = {
            "approved": announcements.filter(is_approved = True),
            "rejected": announcements.filter(is_approved = False).filter(author_id = request.session['_auth_user_id']),
            "unapproved": announcements.filter(is_approved = None).filter(author_id = request.session['_auth_user_id']),
        }
    return render(request, 'farmstemp/mem-announce.html', context)

def sendAnnouncement(bindings, body):
    # ACCOUNT_SID = getenv('TWILIO_ACCOUNT_SID')
    # AUTH_TOKEN = getenv('TWILIO_AUTH_TOKEN')
    # NOTIFY_SERVICE_SID = getenv('TWILIO_NOTIFY_SERVICE_SID')

    # client              = Client(ACCOUNT_SID, AUTH_TOKEN)

    # print("=====> To Bindings :>", bindings, "<: =====")
    # notification = client.notify.services(NOTIFY_SERVICE_SID).notifications.create(
    #     to_binding=bindings,
    #     body=body
    # )
    
    # debug(notification.body)
    ancmt = {
        'address': bindings,
        'body': body
    }
    debug(ancmt)

def memAnnouncements_Approval(request, decision):
    """
    Approves or reject an announcement, sets [is_approved] to either [true] or [false]

    :param decision: "approve" or "reject" depending on the ajax call
    :type decision: String
    """
    if decision:
        idQry = request.POST.get("idList")    
        idList = json.loads(idQry)

        if decision == "approve":
            debug("Messages approved.")
            Mem_Announcement.objects.filter(pk__in=idList).update(is_approved = True)
            messages.success(request, "Messages successfully approved and sent to raisers.", extra_tags='announcement')
            for id in idList:
                ancmt = Mem_Announcement.objects.filter(pk = id).values('title','category','recip_area','mssg')
                addressList = []
                body = ancmt[0]['category'] + ': ' + ancmt[0]['title'] + '\n' + ancmt[0]['mssg']
                # debug(ancmt)
                
                if ancmt[0]['recip_area'] == 'All Raisers':
                    nums = Farm.objects.select_related("hog_raiser").distinct("hog_raiser__contact_no").values('hog_raiser__contact_no')
                else:
                    nums = Farm.objects.select_related("hog_raiser", "area").filter(area__area_name__in = ancmt[0]['recip_area'].split(', ')).distinct("hog_raiser__contact_no").values('hog_raiser__contact_no')
                for address in nums:
                    addressList.append(
                        json.dumps({
                            'binding_type':'sms',
                            'address': address['hog_raiser__contact_no']
                        })
                    )
                if addressList:
                    sendAnnouncement(addressList, body)

            return JsonResponse({"success": "Messages successfully approved and sent to raisers."}, status=200)
    
        elif decision == "reject":
            debug("Messages rejected.")        
            mssg = request.POST.get("mssg")
            Mem_Announcement.objects.filter(pk__in=idList).update(is_approved = False, reject_reason = mssg)
            messages.success(request, "Messages rejected.", extra_tags='announcement')

            return JsonResponse({"success": "Messages rejected."}, status=200)
    
    else:
        debug("There was an error in saving the approval.")
        messages.error(request, "There was an error in saving the approval.", extra_tags='announcement')
        return JsonResponse({"error": "There was an error in saving the approval."}, status=400)
    

def createAnnouncement(request):
    """
    Create announcment
    Defaults to approved if assistant manager
    """

    if request.method == 'POST':
        if(request.POST.getlist("recip_area")):
            autoApprove = ['Assistant Manager']
            if request.user.groups.all()[0].name in autoApprove:
                approvalState = True
                addressList = []
                body = request.POST.get("category") + ': ' + request.POST.get("title") + '\n' + request.POST.get("mssg") 
                if request.POST.getlist("recip_area") == ['All Raisers']:
                    nums = Farm.objects.select_related("hog_raiser").distinct("hog_raiser__contact_no").values('hog_raiser__contact_no')
                else:
                    nums = Farm.objects.select_related("hog_raiser", "area").filter(area__area_name__in = request.POST.getlist("recip_area")).distinct("hog_raiser__contact_no").values('hog_raiser__contact_no')
                for address in nums:
                    addressList.append(
                            json.dumps({
                                'binding_type':'sms',
                                'address': address['hog_raiser__contact_no']
                            })
                        )
                if addressList:
                        sendAnnouncement(addressList, body)
            else:
                approvalState = None

            announcement = Mem_Announcement(
                title = request.POST.get("title"),
                category = request.POST.get("category"),
                recip_area = ", ".join(request.POST.getlist("recip_area")),
                mssg = request.POST.get("mssg"),
                author_id = request.user.id,
                timestamp = now(),
                is_approved = approvalState
            )
            announcement.save()
            messages.success(request, "Announcement sent.", extra_tags='announcement')

            debug(request.POST)
            debug(request.POST.getlist("recip_area"))
            debug(Boolean(request.POST.getlist("recip_area") == ['All Raisers']))
            return redirect('/member-announcements')
        messages.error(request, "Choose at least one recipient area.", extra_tags='announcement')

    announcementForm = MemAnnouncementForm(user=request.user)
    return render(request, 'farmstemp/create-announcement.html', {'announcementForm' : announcementForm})

def viewAnnouncement(request, id):

    if request.method == 'POST':
        reancmt = Mem_Announcement.objects.filter(id = id).first()
        reancmt.title = request.POST.get("title")
        reancmt.category = request.POST.get("category")
        reancmt.recip_area = request.POST.get("recip_area")
        reancmt.mssg = request.POST.get("mssg")
        reancmt.timestamp = now()
        reancmt.is_approved = None
        reancmt.reject_reason = None

        reancmt.save()
        messages.success(request, "Announcement resubmitted.", extra_tags='announcement')
        return redirect('/member-announcements')

    qry = Mem_Announcement.objects.filter(pk = id).values(
        "id",
        "author_id",
        "title",
        "category",
        "recip_area",
        "mssg",
        "timestamp",
        "reject_reason"
    ).first()
    area_choices = []
    for choice in Area.objects.distinct().filter(tech_id = int(request.user.id)).values('area_name'):
        area_choices.append(choice['area_name'])
    context = {
        "announcement":qry,
        'area_choices' : area_choices
    }
    
    return render(request, 'farmstemp/view-announcement.html', context)

def initNotifIDList(request):
    """
    Get from database notification IDs user has seen

    :param request: used to get userID from session to specify which account data to get from
    :type request: request
    :return: notifIDList
    :rtype: list
    """

    notifIDList = [] # initialize list of seen notifications
    try: # get notiflist from database
        userID = request.session['_auth_user_id']
        notifIDList.extend(User.objects.get(id=userID).accountdata.data['notifIDList'])
    except:
        debug('no notifs obtained from database')
    return notifIDList

def getNotifIDs(request):
    """
    Get from database list of all possible notifIDs for the user

    :param request: used to get userID from session to identify which notifications to get 
    :type request: request
    :return: notifIDs
    :rtype: list
    """
    notifIDs = []
    announceTable = Mem_Announcement._meta.db_table
    actFormTable = Activities_Form._meta.db_table
    mortFormTable = Mortality_Form._meta.db_table
    userTable = User._meta.db_table

    userID = request.session['_auth_user_id']
    userGroup = request.user.groups.all()[0].name

    memancmtForms = Mem_Announcement.objects
    activityForms = Activities_Form.objects
    mortalityForms = Mortality_Form.objects

    if userGroup == "Assistant Manager":
        # Announcements
        pendingAnnouncements = memancmtForms.filter(is_approved = None)
        for item in pendingAnnouncements.values():
            notifIDs.append(';'.join([announceTable, str(item['id']), "Pending"]))
        # Tech Inspection
        for tech in Area.objects.distinct("tech_id").values_list("tech_id"):
            technician  = User.objects.filter(id = tech[0]).values("id", "first_name", "last_name").first()
            farmObj = Farm.objects.filter(area__tech_id = tech[0])
            totalCount = farmObj.count()
            if totalCount == 0:
                continue
            inspectCount = farmObj.exclude(last_updated__range=(now() - timedelta(days=7), now())).count()
            notifIDs.append(';'.join([
                userTable, 
                str(technician['id']), 
                "{:.0%}".format(inspectCount/totalCount)
            ]))

    elif userGroup == "Field Technician":
        # Announcements
        rejectedAnnouncement = memancmtForms.filter(is_approved = False).filter(author_id = userID)
        for item in rejectedAnnouncement.values():
            notifIDs.append(';'.join([announceTable, str(item['id']), "Rejected"]))

        # Farm Inspections
        farmTable = Farm._meta.db_table
        areaIDList = []
        for i in Area.objects.filter(tech_id = userID).order_by('id').values_list('id'):
            areaIDList.append(i[0])
        needInspectFarms = Farm.objects.exclude(last_updated__range=(now() - timedelta(days=7), now())).filter(area_id__in=areaIDList).values()
        for item in needInspectFarms:
            notifIDs.append(';'.join([farmTable, str(item['id']), "Inspect"]))

        # Active Incidents
        hogSympTable = Hog_Symptoms._meta.db_table
        farmIDList = []
        for i in Farm.objects.filter(area_id__in=areaIDList).order_by('id').values_list('id'):
            farmIDList.append(i[0])
        activeIncs = Hog_Symptoms.objects.filter(ref_farm_id__in=farmIDList, report_status="Active").values()
        for item in activeIncs:
            notifIDs.append(';'.join([hogSympTable, str(item['id']), "Active"]))

        # Weight Updates
        farmWtTable = Farm_Weight._meta.db_table
        farmIDList = []
        for i in Farm.objects.filter(area_id__in=areaIDList).order_by('id').values_list('id'):
            farmIDList.append(i[0])
        farmWtQry = Farm_Weight.objects.order_by('ref_farm_id', '-date_filed').distinct('ref_farm_id').filter(ref_farm_id__in=farmIDList)
        wt_farmIDList = []
        for i in farmWtQry.values_list('ref_farm_id'):
            wt_farmIDList.append(i[0])        
        no_farmWtList = list(set(wt_farmIDList)-set(farmIDList)) + list(set(farmIDList)-set(wt_farmIDList))
        if wt_farmIDList:
            needWtUpdate = farmWtQry.exclude(date_filed__range=(now()-timedelta(days=120), now())).values()
            for item in needWtUpdate:
                notifIDs.append(';'.join([farmWtTable, str(item['id']), "120days"]))
        if no_farmWtList:
            noFarmWt = Farm.objects.filter(id__in=no_farmWtList).exclude(date_registered__range=(now()-timedelta(days=7), now())).values()
            for item in noFarmWt:
                notifIDs.append(';'.join([Farm._meta.db_table, str(item['id']), "NoWt"]))

        # Activity Forms
        techActFormNotifs = activityForms.filter(is_checked=True).filter(date_added__range=(now() - timedelta(days=120), now())).filter(act_tech_id = userID)
        for item in techActFormNotifs.values():
            notifIDs.append(';'.join([actFormTable, str(item['id']), "Approved"]))
        techActFormNotifs = activityForms.filter(is_checked=False).filter(date_added__range=(now() - timedelta(days=120), now())).filter(act_tech_id = userID)
        for item in techActFormNotifs.values():
            notifIDs.append(';'.join([actFormTable, str(item['id']), "Rejected"]))

    elif userGroup == "Livestock Operation Specialist":
        # Activity Forms
        lopsNotifs = activityForms.filter(is_checked=True).filter(date_added__range=(now() - timedelta(days=120), now()))
        for item in lopsNotifs.values():
            notifIDs.append(';'.join([actFormTable, str(item['id'])]))
        lopsNotifs = activityForms.filter(is_checked=None).filter(date_added__range=(now() - timedelta(days=120), now()))
        for item in lopsNotifs.values():
            notifIDs.append(';'.join([actFormTable, str(item['id']), "Pending"]))

    elif userGroup == "Paiwi Management Staff":
        # Mortality Forms
        pamsNotifs = mortalityForms.filter(date_added__range=(now() - timedelta(days=120), now()))
        for item in pamsNotifs.values():
            notifIDs.append(';'.join([mortFormTable, str(item['id'])]))
    
    elif userGroup == "Extension Veterinarian":
        # Activity Forms
        evetNotifs = activityForms.filter(is_checked=True).filter(date_added__range=(now() - timedelta(days=120), now()))
        for item in evetNotifs.values():
            notifIDs.append(';'.join([actFormTable, str(item['id'])]))
        # Mortality Forms
        evetNotifs = mortalityForms.filter(date_added__range=(now() - timedelta(days=120), now()))
        for item in evetNotifs.values():
            notifIDs.append(';'.join([mortFormTable, str(item['id'])]))

    elif userGroup == "Regional Manager":
        # Tech Inspection
        for tech in Area.objects.distinct("tech_id").values_list("tech_id"):
            technician  = User.objects.filter(id = tech[0]).values("id", "first_name", "last_name").first()
            farmObj = Farm.objects.filter(area__tech_id = tech[0])
            totalCount = farmObj.count()
            inspectCount = farmObj.exclude(last_updated__range=(now() - timedelta(days=7), now())).count()
            notifIDs.append(';'.join([
                userTable, 
                str(technician['id']), 
                "{:.0%}".format(inspectCount/totalCount)
            ]))

    return notifIDs 

def getMemAncmtNotifs(request, notifIDList):
    notifList = []
    new_notifIDList = []
    announceTable = Mem_Announcement._meta.db_table
    # Generate notifications to be displayed
    ## Current tags:
    # string label_class: Classes that will be appended to notif-label. e.g. "notif-urgent"
    # string label: Title of the notification
    # string p: Message of the notification
    # string href: link to the page the user will be sent to if they click on the notification  
    if request.user.groups.all()[0].name == "Assistant Manager":
        pendingAnnouncements = Mem_Announcement.objects.filter(is_approved = None).values()
        count = 0
        for item in pendingAnnouncements:
            notifID = ';'.join([announceTable, str(item['id']), "Pending"])
            new_notifIDList.append(notifID)
            if notifID not in notifIDList:
                count += 1
        if count != 0: 
            notifList.append({
                "label_class": "text-warning",
                "label": "{} pending announcement(s) for approval".format(count),
                "href": "/member-announcements"
            })
    else:
        rejectedAnnouncement = Mem_Announcement.objects.filter(is_approved = False).filter(author_id = request.session['_auth_user_id']).values()
        count = 0
        for item in rejectedAnnouncement:
            notifID = ';'.join([announceTable, str(item['id']), "Rejected"])
            new_notifIDList.append(notifID)
            if notifID not in notifIDList:
                count += 1
        if count != 0:
            notifList.append({
                "label_class": "text-danger",
                "label": "{} Announcement(s) were rejected".format(count),
            })

    return {
        "notifIDList": new_notifIDList,
        "notifList": notifList
    }

def getActFormsNotifs(request, notifIDList):
    """
    Get notifications on Activity Forms for a specific user

    :param notifIDList: List of notifications already seen by the user
    :type notifIDList: list
    """
    notifList = []
    new_notifIDList = []
    tableName = Activities_Form._meta.db_table
    userGroup = request.user.groups.all()[0].name
    activityForms = Activities_Form.objects

    if userGroup == "Field Technician":
        userID = request.session['_auth_user_id']
        techNotifs = activityForms.filter(date_added__range=(now() - timedelta(days=120), now()))
        qry = techNotifs.filter(is_checked = True).filter(act_tech_id = userID)
        count = 0
        for item in qry.values():
            notifID = ';'.join([tableName, str(item['id']), "Approved"])
            new_notifIDList.append(notifID)
            if notifID not in notifIDList:
                count = count + 1
        if count != 0:
            notifList.append({
                "label_class": "text-success",
                "notificationID": notifID,
                "label": "{} recently approved activity form(s)".format(count),
                "href": "/forms-approval"
            })

        qry = techNotifs.filter(is_checked = False).filter(act_tech_id = userID)
        count = 0
        for item in qry.values():
            notifID = ';'.join([tableName, str(item['id']), "Rejected"])
            new_notifIDList.append(notifID)
            if notifID not in notifIDList:
                count = count + 1
        if count != 0:
            notifList.append({
                "label_class": "text-success",
                "notificationID": notifID,
                "label": "{} recently rejected activity form(s)".format(count),
                "href": "/forms-approval"
            })
        return {
            "notifIDList": new_notifIDList,
            "notifList": notifList
        }
    elif userGroup == "Livestock Operation Specialist":
        lopsNotifs = activityForms.filter(is_checked = None).filter(date_added__range=(now() - timedelta(days=120), now()))
        # notification for newly submitted activity forms
        count = 0
        for item in lopsNotifs.values():
            notifID = ';'.join([tableName, str(item['id']), "Pending"])
            new_notifIDList.append(notifID)
            if notifID not in notifIDList:
                count = count + 1
        if count != 0:
            notifList.append({
                "label_class": "text-warning",
                "notificationID": notifID,
                "label": "{} Activity Form(s) are pending approval".format(count),
                "href": "/forms-approval"
            })

    actForms = activityForms.filter(is_checked=True).filter(date_added__range=(now() - timedelta(days=120), now()))
    count = 0
    for item in actForms.values():
        notifID = ';'.join([tableName, str(item['id'])])
        new_notifIDList.append(notifID)
        if notifID not in notifIDList:
            count = count + 1
    if count != 0:
        notifList.append({
            "label_class": "text-success",
            "notificationID": notifID,
            "label": "{} recently approved activity form(s)".format(count),
            "href": "/forms-approval"
        })

    return {
        "notifIDList": new_notifIDList,
        "notifList": notifList
    }

def getMortFormsNotifs(request, notifIDList):
    """
    Get notifications on Mortality Forms for a specific user

    :param notifIDList: List of notifications already seen by the user
    :type notifIDList: list
    """
    notifList = []
    new_notifIDList = []
    mortFormTable = Mortality_Form._meta.db_table
    mortalityForms = Mortality_Form.objects

    mortForms = mortalityForms.filter(date_added__range=(now() - timedelta(days=120), now()))
    # notification for pending assistant manager approval
    count = 0
    for item in mortForms.values():
        notifID = ';'.join([mortFormTable, str(item['id'])])
        new_notifIDList.append(notifID)
        if notifID not in notifIDList:
            count = count + 1
    if count != 0:
        notifList.append({
            "label_class": "text-success",
            "notificationID": notifID,
            "label": "{} recently created mortality record(s)".format(count),
            "href": "/forms-approval"
        })

    return {
        "notifIDList": new_notifIDList,
        "notifList": notifList
    }
 
def getFarmInspectNotifs(request, notifIDList):
    notifList = []
    new_notifIDList = []
    farmTable = Farm._meta.db_table
    areaIDList = []
    for i in Area.objects.filter(tech_id = request.session['_auth_user_id']).order_by('id').values_list('id'):
        areaIDList.append(i[0])

    needInspectFarms = Farm.objects.exclude(last_updated__range=(now() - timedelta(days=7), now())).filter(area_id__in=areaIDList).values()
    count = 0
    for item in needInspectFarms:
        notifID = ';'.join([farmTable, str(item['id']), "Inspect"])
        new_notifIDList.append(notifID)
        if notifID not in notifIDList:
            count += 1
            
    if count != 0:
        notifList.append({
            "label_class": "text-danger",
            "label": "{} Farm(s) in need of inspection".format(count),
            "href": "/farms"
        })
    
    return {
        "notifIDList": new_notifIDList,
        "notifList": notifList
    }

def getActiveIncsNotifs(request, notifIDList):
    notifList = []
    new_notifIDList = []
    hogSympTable = Hog_Symptoms._meta.db_table
    areaIDList = []
    for i in Area.objects.filter(tech_id = request.session['_auth_user_id']).order_by('id').values_list('id'):
        areaIDList.append(i[0])

    farmIDList = []
    for i in Farm.objects.filter(area_id__in=areaIDList).order_by('id').values_list('id'):
        farmIDList.append(i[0])

    activeIncs = Hog_Symptoms.objects.filter(ref_farm_id__in=farmIDList, report_status="Active").values()
    count = 0
    for item in activeIncs:
        notifID = ';'.join([hogSympTable, str(item['id']), "Active"])
        new_notifIDList.append(notifID)
        if notifID not in notifIDList:
            count += 1
            
    if count != 0:
        notifList.append({
            "label_class": "text-danger",
            "label": "{} Incidents(s) are currently active".format(count),
            "href": "/health-symptoms"
        })
    
    return {
        "notifIDList": new_notifIDList,
        "notifList": notifList
    }

def getWtUpdateNotifs(request, notifIDList):
    notifList = []
    new_notifIDList = []
    farmWtTable = Farm_Weight._meta.db_table
    areaIDList = []
    for i in Area.objects.filter(tech_id = request.session['_auth_user_id']).order_by('id').values_list('id'):
        areaIDList.append(i[0])

    farmIDList = []
    for i in Farm.objects.filter(area_id__in=areaIDList).order_by('id').values_list('id'):
        farmIDList.append(i[0])

    farmWtQry = Farm_Weight.objects.order_by('ref_farm_id', '-date_filed').distinct('ref_farm_id').filter(ref_farm_id__in=farmIDList)
    wt_farmIDList = []
    for i in farmWtQry.values_list('ref_farm_id'):
        wt_farmIDList.append(i[0])
    
    no_farmWtList = list(set(wt_farmIDList)-set(farmIDList)) + list(set(farmIDList)-set(wt_farmIDList))

    # 120 day update
    if wt_farmIDList:
        needWtUpdate = farmWtQry.exclude(date_filed__range=(now()-timedelta(days=120), now())).values()
        count = 0
        for item in needWtUpdate:
            notifID = ';'.join([farmWtTable, str(item['id']), "120days"])
            new_notifIDList.append(notifID)
            if notifID not in notifIDList:
                count += 1
        if count != 0:
            notifList.append({
                "label_class": "text-danger",
                "label": "{} Farm(s)' weight record have not been updated in 120 days".format(count),
                "href": "/health-symptoms"
            })
    # 7 day no weight
    if no_farmWtList:
        noFarmWt = Farm.objects.filter(id__in=no_farmWtList).exclude(date_registered__range=(now()-timedelta(days=7), now())).values()
        count = 0
        for item in noFarmWt:
            notifID = ';'.join([Farm._meta.db_table, str(item['id']), "NoWt"])
            new_notifIDList.append(notifID)
            if notifID not in notifIDList:
                count += 1
        if count != 0:
            notifList.append({
                "label_class": "text-danger",
                "label": "{} Farm(s) still do not have weight records".format(count),
                "href": "/health-symptoms"
            })
    return {
        "notifIDList": new_notifIDList,
        "notifList": notifList
    }

def getTechInspectNotifs(request, notifIDList):
    notifList = []
    new_notifIDList = []
    userTable = User._meta.db_table

    for tech in Area.objects.distinct("tech_id").values_list("tech_id"):
        technician  = User.objects.filter(id = tech[0]).values("id", "first_name", "last_name").first()
        farmObj = Farm.objects.filter(area__tech_id = tech[0])
        totalCount = farmObj.count()
        if totalCount == 0:
                continue
        inspectCount = farmObj.exclude(last_updated__range=(now() - timedelta(days=7), now())).count()

        inspectPercent = inspectCount/totalCount

        notifID = ';'.join([
            userTable, 
            str(technician['id']), 
            "{:.0%}".format(inspectPercent)
        ])
        new_notifIDList.append(notifID)

        if (inspectPercent > 0.25) and (notifID not in notifIDList):
            notifList.append({
                "label_class": "text-danger",
                "label": "{:.0%} of {} {}'s farms need inspecton".format(inspectPercent, technician['first_name'], technician['last_name']),
            })

    return {
        "notifIDList": new_notifIDList,
        "notifList": notifList
    }

def getNotifications(request):
    """
    Collects all notifications from different tables
    """
    
    notifIDList = []
    notifList = []

    userGroup = request.user.groups.all()[0].name
    request.session['notifIDList'] = initNotifIDList(request)
    notifIDList = request.session['notifIDList']
    memAncmtNotifs = getMemAncmtNotifs(request, notifIDList)    
    
    # technician specific functions
    if userGroup == "Field Technician":
        frmInspcNotifs = getFarmInspectNotifs(request, notifIDList)
        actIncdsNotifs = getActiveIncsNotifs(request, notifIDList)
        wtUpdateNotifs = getWtUpdateNotifs(request, notifIDList)
        actFormsNotifs = getActFormsNotifs(request, notifIDList)
        notifIDList += frmInspcNotifs['notifIDList'] + actIncdsNotifs['notifIDList'] + wtUpdateNotifs['notifIDList'] + actFormsNotifs["notifIDList"]
        notifList += frmInspcNotifs['notifList'] + actIncdsNotifs['notifList'] + wtUpdateNotifs['notifList'] + actFormsNotifs["notifList"]
    
    elif userGroup == "Livestock Operation Specialist":
        actFormsNotifs = getActFormsNotifs(request, notifIDList)
        notifIDList += actFormsNotifs["notifIDList"]
        notifList += actFormsNotifs["notifList"]

    elif userGroup == "Paiwi Management Staff":
        mrtFormsNotifs = getMortFormsNotifs(request, notifIDList)
        notifIDList += mrtFormsNotifs["notifIDList"]
        notifList += mrtFormsNotifs["notifList"]

    elif userGroup == "Extension Veterinarian":
        actFormsNotifs = getActFormsNotifs(request, notifIDList)
        mrtFormsNotifs = getMortFormsNotifs(request, notifIDList)
        notifIDList +=  actFormsNotifs["notifIDList"] + mrtFormsNotifs["notifIDList"]
        notifList += actFormsNotifs["notifList"] + mrtFormsNotifs["notifList"]

    elif userGroup == "Assistant Manager":
        tchNspctNotifs = getTechInspectNotifs(request, notifIDList)
        notifIDList += tchNspctNotifs["notifIDList"]
        notifList += tchNspctNotifs["notifList"] 

    elif userGroup == "Regional Manager":
        tchNspctNotifs = getTechInspectNotifs(request, notifIDList)
        notifIDList += tchNspctNotifs["notifIDList"]
        notifList += tchNspctNotifs["notifList"]

    notifIDList += memAncmtNotifs["notifIDList"]
    notifList += memAncmtNotifs["notifList"]

    request.session['notifIDList'] = notifIDList # overwrite old notifIDList with new one 

    return render(request, 'partials/notifications.html', {"notifList": notifList})

def syncNotifications(request):
    """
    Saving notifications data from sessions to database
    """

    sessionNotifs = []
    userID = request.session['_auth_user_id']
    
    try:
        sessionNotifs.extend(request.session['notifIDList'])
    except:
        debug('no notifs from session found')
        return HttpResponse({"error": "no notifs from session found"}, status=404) # no way for sessions notifs to be empty because this will always go after getNotifications

    try:
        User.objects.get(id=userID).accountdata.data
        User.objects.get(id=userID).accountdata.data['notifIDList']
    except:
        AccountData(
            user_id = userID,
            data = {'notifIDList':[]}
        ).save()
    
    try:
        User.objects.get(id=userID).accountdata.data['notifIDList']
    except:
        notifQry = AccountData.objects.get(user_id = userID)
        notifQry.data['notifIDList'] = []
        notifQry.save()

    if (Counter(User.objects.get(id=userID).accountdata.data['notifIDList']) != Counter(sessionNotifs)):
        new_dbNotifs = [] # inside if statement so that it does not overwrite accountData.notifIDList
        if len(sessionNotifs) != 0: #if sessionNotifs is not empty
            notifIDs = getNotifIDs(request)
            for notifID in notifIDs:
                if notifID in sessionNotifs:
                    if notifID.find("Rejected") != -1 and notifID.find("announce") != -1:
                        try:
                            Mem_Announcement.objects.filter(id=int(notifID.split(';')[1])).delete()
                        except:
                            debug("could not delete Announcement ID: " + str(notifID.split(';')[1]))
                    else:
                        new_dbNotifs.append(notifID)
    
    try: # try to save user session 
        notifQry = AccountData.objects.get(user_id = userID)
        notifQry.data['notifIDList'] = new_dbNotifs
        notifQry.save()
    except:
        debug('session was not saved to database')

    return HttpResponse({"success":"session and database synced"}, status=200)
    

def countNotifications(request):
    totalNotifs = 0
    notifIDList = initNotifIDList(request)

    userGroup = request.user.groups.all()[0].name

    memAncmtNotifs = getMemAncmtNotifs(request, notifIDList)

    # technician specific functions
    if userGroup == "Field Technician":
        frmInspcNotifs = getFarmInspectNotifs(request, notifIDList)
        actIncdsNotifs = getActiveIncsNotifs(request, notifIDList)
        wtUpdateNotifs = getWtUpdateNotifs(request, notifIDList)
        actFormsNotifs = getActFormsNotifs(request, notifIDList)
        totalNotifs += len(frmInspcNotifs['notifList']) + len(actIncdsNotifs['notifList']) + len(wtUpdateNotifs['notifList']) + len(actFormsNotifs["notifList"])
    
    elif userGroup == "Livestock Operation Specialist":
        actFormsNotifs = getActFormsNotifs(request, notifIDList)
        totalNotifs += len(actFormsNotifs["notifList"])
            

    elif userGroup == "Paiwi Management Staff":
        mrtFormsNotifs = getMortFormsNotifs(request, notifIDList)
        totalNotifs += len(mrtFormsNotifs["notifList"])

    elif userGroup == "Extension Veterinarian":
        actFormsNotifs = getActFormsNotifs(request, notifIDList)
        mrtFormsNotifs = getMortFormsNotifs(request, notifIDList)
        totalNotifs += len(actFormsNotifs["notifList"]) + len(mrtFormsNotifs["notifList"])

    elif userGroup == "Assistant Manager":
        tchNspctNotifs = getTechInspectNotifs(request, notifIDList)
        totalNotifs += len(tchNspctNotifs["notifList"])

    elif userGroup == "Regional Manager":
        tchNspctNotifs = getTechInspectNotifs(request, notifIDList)
        totalNotifs += len(tchNspctNotifs["notifList"])
    
    totalNotifs += len(memAncmtNotifs["notifList"])
            

    return HttpResponse(str(totalNotifs), status=200)

def computeBioscore(farmID, intbioID, extbioID):
    """
    Helper function for calculating Internal and External biosec scores of a Farm.
    
    BIOSCORE = ( (total measure points + total checklist points) / (total points - N/A))
    """

    # debug("in computeIntBio()/n")

    # debug("param // farmID -- " + str(farmID))
    # debug("param // intbioID -- " + str(intbioID))
    # debug("param // extbioID -- " + str(extbioID))

    intbio_score = 0
    extbio_score = 0

    total_measures = 0
    total_checks = 0
    total_no_input = 0
    total_NA = 0

    # (1) INTERNAL BIOSEC SCORE
    if intbioID is not None: 
        # Get Intbio record based in farmID & biosec IDs
        intBio = InternalBiosec.objects.filter(id=intbioID, ref_farm_id=farmID).first()

        # total Internal Biomeasures
        """
        ----------------------------
        int_val | equivalent | score
        ----------------------------
        0       | Yes        | +1 total_measures
        1       | No         | 0  total_measures
        2       | N/A        | +1 total_NA
        ----------------------------
        Total: /3 fields   
        """
        intmeasList = [intBio.isol_pen, intBio.foot_dip]

        for measure in intmeasList:
            if measure == 0:
                total_measures += 1
            elif measure == 1:
                total_measures += 0
            else:
                total_NA += 1

        waste_mgt_list = ['Septic Tank', 'Biogas', 'Other']
        if intBio.waste_mgt in waste_mgt_list:
            total_measures += 1
        else:
            total_NA += 1
        
        # total Internal Biochecklist
        """
        ----------------------------
        int_val | equivalent | score
        ----------------------------
        0       | Yes        | +2 total_checks
        1       | No         | 0  total_checks
        2       | N/A        | +1 total_NA
        ----------------------------
        Total: /2 fields   
        """
        intcheckList = [intBio.disinfect_prem, intBio.disinfect_vet_supp]

        for check in intcheckList:
            if check == 0:
                total_checks += 2
            elif check == 1:
                total_checks += 0
            # elif check == 3:
            #     total_no_input += 
            else:
                total_NA += 2

        # debug("intbio // total_measures -- " + str(total_measures))
        # debug("intbio // total_checks -- " + str(total_checks))
        # debug("intbio // total_NA -- " + str(total_NA))

        # compute BIOSCORE and round up to 2 decimal places
        intbio_score = ((total_measures + total_checks) / (7 - total_NA)) * 100
        intbio_score = round(intbio_score,2)
        # debug("INTBIO_SCORE -- " + str(intbio_score))


    # (2) EXTERNAL BIOSEC SCORE
    if extbioID is not None:

        total_measures = 0
        total_checks = 0
        total_NA = 0

        # Get Extbio record based in farmID & biosec IDs
        extBio = ExternalBiosec.objects.filter(id=extbioID, ref_farm_id=farmID).first()

        # total External Biomeasures
        """
        ----------------------------
        int_val | equivalent | score
        ----------------------------
        0       | Yes        | +1 total_measures
        1       | No         | 0  total_measures
        2       | N/A        | +1 total_NA
        ----------------------------
        Total: /3 fields   
        """
        extmeasList = [extBio.bird_proof, extBio.perim_fence, extBio.fiveh_m_dist]

        for measure in extmeasList:
            if measure == 0:
                total_measures += 1
            elif measure == 1:
                total_measures += 0
            else:
                total_NA += 1

        
        # total External Biochecklist
        """
        ----------------------------
        int_val | equivalent | score
        ----------------------------
        0       | Yes        | +2 total_checks
        1       | No         | 0  total_checks
        2       | N/A        | +1 total_NA
        ----------------------------
        Total: /6 fields   
        """
        extcheckList = [extBio.prvdd_foot_dip, extBio.prvdd_alco_soap, extBio.obs_no_visitors, extBio.prsnl_dip_footwear, extBio.prsnl_sanit_hands, extBio.chg_disinfect_daily]

        for check in extcheckList:
            if check == 0:
                total_checks += 2
            elif check == 1:
                total_checks += 0
            else:
                total_NA += 2

        # debug("extbio // total_measures -- " + str(total_measures))
        # debug("extbio // total_checks -- " + str(total_checks))
        # debug("extbio // total_NA -- " + str(total_NA))

        # compute BIOSCORE and round up to 2 decimal places
        extbio_score = ((total_measures + total_checks) / (15 - total_NA)) * 100
        extbio_score = round(extbio_score,2)
        # debug("EXTBIO_SCORE -- " + str(extbio_score))

    # returns a tuple; access using "var_name[0]" and "var_name[1]"
    return intbio_score, extbio_score


# REPORTS for Module 1

def farmsAssessment(request):
    # debug("TEST LOG: in farmsAssessment Report/n")

    """
    Gets all Farm records within existing dates and all Areas due to no selected filters in dropdown

    (1) earliest data, recent data of Farm 
    (2) all Area records
    (3) Farm details
        - farm code, raiser full name, address, technician assigned, num pigs, num pens, 
        - intbio score, extbio score, last_updated (in Farm/Biosec?)
    """

    # for checking if filters were used in the displayed Report
    isFiltered = False

    # for setting Date input filters to today's date
    dateToday = datetime.now(timezone.utc)

    # (1) earliest and most recent last_updated in Farm
    dateASC = Farm.objects.only("last_updated").order_by('last_updated').first()
    dateDESC = Farm.objects.only("last_updated").order_by('-last_updated').first()

    # (2) all Area records
    areaQry = Area.objects.all()

    # Get technician name assigned per Farm
    farmQry = Farm.objects.all().prefetch_related("area", "area__tech").order_by("id")
    # debug("techQry -- " + str(farmQry.query))

    if not farmQry.exists(): # (ERROR) No farm records found.
        messages.error(request, "No farm records found.", extra_tags="farmass-report")
        return render(request, 'farmstemp/rep-farms-assessment.html', {"isFiltered": isFiltered,'areaList': areaQry,'dateStart': dateToday,'dateEnd': dateToday})

    # debug("list for -- Farm > Area > User (tech)")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        # print(techObject["name"])
        techList.append(techObject)
    # debug(techList)    


    # (3) Farm details 
    qry = Farm.objects.select_related('hog_raiser', 'area', 'intbio', 'extbio').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        farm_area = F("area__area_name"),
        intbioID = F("intbio__id"),
        extbioID = F("extbio__id")
        ).values(
            "id",
            "fname",
            "lname", 
            "farm_address",
            "farm_area",
            "total_pigs",
            "num_pens",
            "last_updated",
            "intbioID",
            "extbioID"
            ).order_by("id")
    # debug(qry)

    if not qry.exists(): 
        messages.error(request, "No farm records found.", extra_tags="farmass-report")
        return render(request, 'farmstemp/rep-farms-assessment.html', {"isFiltered": isFiltered,'areaList': areaQry,'dateStart': dateToday,'dateEnd': dateToday})

    farmsData = []
    total_pigs = 0
    total_pens = 0
    ave_pigs = 0
    ave_pens = 0
    ave_intbio = 0
    ave_extbio = 0
    for f in qry:

        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], f["intbioID"], f["extbioID"])

        farmObject = {
            "code":  f["id"],
            "raiser": " ".join((f["fname"],f["lname"])),
            "address": f["farm_address"],
            "area": str(f["farm_area"]),
            "pigs": str(f["total_pigs"]),
            "pens": str(f["num_pens"]),
            "updated": f["last_updated"],
            "intbio_score": str(biosec_score[0]),
            "extbio_score": str(biosec_score[1])
        }
        farmsData.append(farmObject)

        total_pigs += f["total_pigs"]
        total_pens += f["num_pens"]

        ave_intbio += biosec_score[0]
        ave_extbio += biosec_score[1]

    # debug(farmsData)

    # combine farm + tech lists into one list
    farmtechList = zip(farmsData, techList)

    # compute for -- total (pigs, pens) and ave columns (pigs, pens, intbio, extbio)
    ave_pigs   = round((total_pigs / len(farmsData)), 2)
    ave_pens   = round((total_pens / len(farmsData)), 2)
    ave_intbio = round((ave_intbio / len(farmsData)), 2)
    ave_extbio = round((ave_extbio / len(farmsData)), 2)
    
    farmTotalAve = {
        "total_pigs": total_pigs,
        "total_pens": total_pens,
        "ave_pigs": ave_pigs,
        "ave_pens": ave_pens,
        "ave_intbio": ave_intbio,
        "ave_extbio": ave_extbio,
    }


    return render(request, 'farmstemp/rep-farms-assessment.html', {"isFiltered": isFiltered,"farmTotalAve": farmTotalAve, 'dateStart': dateToday,'dateEnd': dateToday,'areaList': areaQry,'farmtechList': farmtechList})


def filter_farmsAssessment(request, startDate, endDate, areaName):
    """
    Gets Farm records based on (1) date range and (2) area name filters.

    (1) earliest data, recent data of Farm 
    (2) Area selected in dropdown (?)
    (3) Farm details
        - farm code, raiser full name, address, technician assigned, num pigs, num pens, 
        - intbio score, extbio score, last_updated (in Farm/Biosec?)
    """

    # debug("TEST LOG: in filter_farmsAssessment Report()/n")

    # debug("URL params:")
    # debug("startDate -- " + startDate)
    # debug("endDate -- " + endDate)
    # debug("areaName -- " + areaName)


    # convert str Dates to date type; then to a timezone-aware datetime
    sDate = make_aware(datetime.strptime(startDate, "%Y-%m-%d")) 
    eDate = make_aware(datetime.strptime(endDate, "%Y-%m-%d")) + timedelta(1) # add 1 day to endDate

    # debug("converted sDate -- " + str(type(sDate)))
    # debug("converted eDate -- " + str(type(eDate)))

    # to revert endDate to same user date input
    truEndDate = eDate - timedelta(1)

    # for checking if filters were used in the displayed Report
    isFiltered = True

    # (2) all Area records for dropdown
    areaQry = Area.objects.all()


    # (3) Farm details based on selected filters
    if areaName == "All": # (CASE 1) search only by date range
        debug("TRACE: in areaName == 'All'")

        # Get technician name assigned per Farm
        # Farm > Area > User (tech)
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).all().prefetch_related("area", "area__tech").order_by("id")

        if not farmQry.exists(): # (ERROR) No farm records found.
            messages.error(request, "No farm records found.", extra_tags="farmass-report")
            return render(request, 'farmstemp/rep-farms-assessment.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})

        qry = Farm.objects.filter(last_updated__range=(sDate, eDate)).select_related('hog_raiser', 'area').annotate(
            fname=F("hog_raiser__fname"), 
            lname=F("hog_raiser__lname"), 
            farm_area = F("area__area_name"),
            intbioID = F("intbio__id"),
            extbioID = F("extbio__id")
            ).values(
                "id",
                "fname",
                "lname", 
                "farm_address",
                "farm_area",
                "total_pigs",
                "num_pens",
                "last_updated",
                "intbioID",
                "extbioID"
                ).order_by("id")
    else: # (CASE 2) search by BOTH date range and areaName
        debug("TRACE: in else/ filter_farmsAssessment")

        # Get technician name assigned per Farm
        # Farm > Area > User (tech)
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).filter(area__area_name=areaName).all().prefetch_related("area", "area__tech").order_by("id")

        if not farmQry.exists(): # (ERROR) No farm records found.
            messages.error(request, "No farm records found.", extra_tags="farmass-report")
            return render(request, 'farmstemp/rep-farms-assessment.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})

        qry = Farm.objects.filter(last_updated__range=(sDate, eDate)).filter(area__area_name=areaName).select_related('hog_raiser', 'area').annotate(
            fname=F("hog_raiser__fname"), 
            lname=F("hog_raiser__lname"), 
            farm_area = F("area__area_name"),
            intbioID = F("intbio__id"),
            extbioID = F("extbio__id")
            ).values(
                "id",
                "fname",
                "lname", 
                "farm_address",
                "farm_area",
                "total_pigs",
                "num_pens",
                "last_updated",
                "intbioID",
                "extbioID"
                ).order_by("id")
   
    # debug(qry)

    if not qry.exists(): 
        messages.error(request, "No farm records found.", extra_tags="farmass-report")
        return render(request, 'farmstemp/rep-farms-assessment.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})

    # debug("list for -- Farm > Area > User (tech)")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        # print(techObject["name"])
        techList.append(techObject)
    # debug(techList)  

    farmsData = []
    total_pigs = 0
    total_pens = 0
    ave_pigs = 0
    ave_pens = 0
    ave_intbio = 0
    ave_extbio = 0
    for f in qry:

        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], f["intbioID"], f["extbioID"])

        farmObject = {
            "code":  f["id"],
            "raiser": " ".join((f["fname"],f["lname"])),
            "address": f["farm_address"],
            "area": str(f["farm_area"]),
            "pigs": str(f["total_pigs"]),
            "pens": str(f["num_pens"]),
            "updated": f["last_updated"],
            "intbio_score": str(biosec_score[0]),
            "extbio_score": str(biosec_score[1])
        }
        farmsData.append(farmObject)

        total_pigs += f["total_pigs"]
        total_pens += f["num_pens"]

        ave_intbio += biosec_score[0]
        ave_extbio += biosec_score[1]

    # debug(farmsData)

    # combine farm + tech lists into one list
    farmtechList = zip(farmsData, techList)

    # compute for -- total (pigs, pens) and ave columns (pigs, pens, intbio, extbio)
    ave_pigs   = round((total_pigs / len(farmsData)), 2)
    ave_pens   = round((total_pens / len(farmsData)), 2)
    ave_intbio = round((ave_intbio / len(farmsData)), 2)
    ave_extbio = round((ave_extbio / len(farmsData)), 2)
    
    farmTotalAve = {
        "total_pigs": total_pigs,
        "total_pens": total_pens,
        "ave_pigs": ave_pigs,
        "ave_pens": ave_pens,
        "ave_intbio": ave_intbio,
        "ave_extbio": ave_extbio,
    }

    return render(request, 'farmstemp/rep-farms-assessment.html', {"areaName": areaName, "isFiltered": isFiltered,"farmTotalAve": farmTotalAve,'dateStart': sDate,'dateEnd': truEndDate,'areaList': areaQry,'farmtechList': farmtechList})


def getBioStr(bioInt):
    """
    Helper function for converting an integer biosec field to corresponding string value.
    """

    if bioInt == 0:
        return "Yes"
    elif bioInt == 1:
        return "No"
    else:
        return "N/A"


def intBiosecurity(request):
    # debug("TEST LOG: in intBiosecurity Report/n")

    """
    Gets current Internal Biosecurity record for each Farm within existing dates and all Areas due to no selected filters in dropdown.

    (1) earliest data, recent data of Farm 
    (2) all Area records
    (3) Farm details
        - farm code, raiser full name, area, technician assigned 
        - (IntBiosec) isol_pen, foot_dip, waste_mgt, disinfect_prem, disinfect_vet_supp, last_updated
        - IntBiosec score
    """

    # for checking if filters were used in the displayed Report
    isFiltered = False

    # for setting Date input filters to today's date
    dateToday = datetime.now(timezone.utc)

    # (1) earliest and most recent last_updated in Farm
    dateASC = Farm.objects.only("last_updated").order_by('last_updated').first()
    dateDESC = Farm.objects.only("last_updated").order_by('-last_updated').first()

    # (2) all Area records
    areaQry = Area.objects.all()

    # Get technician name assigned per Farm
    farmQry = Farm.objects.all().prefetch_related("area", "area__tech").order_by("id")
    # debug("techQry -- " + str(farmQry.query))

    if not farmQry.exists(): # (ERROR) No Internal biosecurity records found.
        messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
        return render(request, 'farmstemp/rep-int-biosec.html', {"isFiltered": isFiltered,'areaList': areaQry,'dateStart': dateToday,'dateEnd': dateToday})

    # debug("list for -- Field Technicians")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        # print(techObject["name"])
        techList.append(techObject)
    # debug(techList)    


    # (3) Farm details
    qry = Farm.objects.select_related('hog_raiser', 'area', 'intbio', 'extbio').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        farm_area = F("area__area_name"),
        intbioID = F("intbio__id"),
        intbio_isol_pen = F("intbio__isol_pen"),
        intbio_foot_dip = F("intbio__foot_dip"),
        intbio_waste_mgt = F("intbio__waste_mgt"),
        intbio_disinfect_prem = F("intbio__disinfect_prem"),
        intbio_disinfect_vet_supp = F("intbio__disinfect_vet_supp")
        ).values(
            "id",
            "fname",
            "lname", 
            "farm_area",
            "last_updated",
            "intbioID",
            "intbio_isol_pen",
            "intbio_foot_dip",
            "intbio_waste_mgt",
            "intbio_disinfect_prem",
            "intbio_disinfect_vet_supp"
            ).order_by("id")
    # debug(qry)

    if not qry.exists(): #(ERROR) No Internal biosecurity records found.
        messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
        return render(request, 'farmstemp/rep-int-biosec.html', {"isFiltered": isFiltered,'areaList': areaQry,'dateStart': dateToday,'dateEnd': dateToday})

    farmsData = []
    ave_intbio = 0

    for f in qry:

        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], f["intbioID"], None)

        farmObject = {
            "code":  f["id"],
            "raiser": " ".join((f["fname"],f["lname"])),
            "area": str(f["farm_area"]),
            "updated": f["last_updated"],
            "intbio_score": str(biosec_score[0]),
            "intbio_isol_pen": getBioStr(f["intbio_isol_pen"]),
            "intbio_foot_dip": getBioStr(f["intbio_foot_dip"]),
            "intbio_waste_mgt": f["intbio_waste_mgt"],
            "intbio_disinfect_prem": getBioStr(f["intbio_disinfect_prem"]),
            "intbio_disinfect_vet_supp": getBioStr(f["intbio_disinfect_vet_supp"]),
        }
        farmsData.append(farmObject)

        ave_intbio += biosec_score[0]

    # debug(farmsData)

    # combine farm + tech lists into one list
    farmtechList = zip(farmsData, techList)

    # compute for -- ave column (intbio)
    ave_intbio = ave_intbio / len(farmsData)
    
    farmTotalAve = {
        "ave_intbio": round(ave_intbio, 2),
    }


    return render(request, 'farmstemp/rep-int-biosec.html', {"isFiltered": isFiltered,"farmTotalAve": farmTotalAve, 'dateStart': dateToday,'dateEnd': dateToday,'areaList': areaQry,'farmtechList': farmtechList})


def filter_intBiosec(request, startDate, endDate, areaName):
    # debug("TEST LOG: in filter_intBiosec Report/n")

    """
    Gets Internal Biosecurity records for each Farm based on (1) date range and (2) area name.

    (1) all Area records
    (2) Farm and Internal Biosec details
        - farm code, raiser full name, area, technician assigned 
        - (IntBiosec) isol_pen, foot_dip, waste_mgt, disinfect_prem, disinfect_vet_supp, last_updated
        - IntBiosec score
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

        # Get technician name assigned per Farm
        # Farm > Area > User (tech)
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).all().prefetch_related("area", "area__tech").order_by("id")

        if not farmQry.exists(): # (ERROR) No Internal biosecurity records found.
            messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
            return render(request, 'farmstemp/rep-int-biosec.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})


        qry = Farm.objects.filter(last_updated__range=(sDate, eDate)).select_related('hog_raiser', 'area').annotate(
                fname=F("hog_raiser__fname"), 
                lname=F("hog_raiser__lname"), 
                farm_area = F("area__area_name"),
                intbioID = F("intbio__id"),
                intbio_isol_pen = F("intbio__isol_pen"),
                intbio_foot_dip = F("intbio__foot_dip"),
                intbio_waste_mgt = F("intbio__waste_mgt"),
                intbio_disinfect_prem = F("intbio__disinfect_prem"),
                intbio_disinfect_vet_supp = F("intbio__disinfect_vet_supp")
                ).values(
                    "id",
                    "fname",
                    "lname", 
                    "farm_area",
                    "last_updated",
                    "intbioID",
                    "intbio_isol_pen",
                    "intbio_foot_dip",
                    "intbio_waste_mgt",
                    "intbio_disinfect_prem",
                    "intbio_disinfect_vet_supp"
                    ).order_by("id")

    else: # (CASE 2) search by BOTH date range and areaName
        debug("TRACE: in else/")

        # Get technician name assigned per Farm
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).filter(area__area_name=areaName).all().prefetch_related("area", "area__tech").order_by("id")

        if not farmQry.exists(): # (ERROR) No Internal biosecurity records found.
            messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
            return render(request, 'farmstemp/rep-int-biosec.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})

        qry = Farm.objects.filter(last_updated__range=(sDate, eDate)).filter(area__area_name=areaName).select_related('hog_raiser', 'area').annotate(
            fname=F("hog_raiser__fname"), 
            lname=F("hog_raiser__lname"), 
            farm_area = F("area__area_name"),
            intbioID = F("intbio__id"),
            intbio_isol_pen = F("intbio__isol_pen"),
            intbio_foot_dip = F("intbio__foot_dip"),
            intbio_waste_mgt = F("intbio__waste_mgt"),
            intbio_disinfect_prem = F("intbio__disinfect_prem"),
            intbio_disinfect_vet_supp = F("intbio__disinfect_vet_supp")
            ).values(
                "id",
                "fname",
                "lname", 
                "farm_area",
                "last_updated",
                "intbioID",
                "intbio_isol_pen",
                "intbio_foot_dip",
                "intbio_waste_mgt",
                "intbio_disinfect_prem",
                "intbio_disinfect_vet_supp"
                ).order_by("id")


    if not qry.exists(): # (ERROR) No Internal biosecurity records found.
        messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
        return render(request, 'farmstemp/rep-int-biosec.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})
        
    # format Technician names per Farm
    # debug("list for -- Field Technicians")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        # print(techObject["name"])
        techList.append(techObject)
    # debug(techList)   

    farmsData = []
    ave_intbio = 0

    # (2) format Farm and Biosec details
    for f in qry:
        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], f["intbioID"], None)

        farmObject = {
            "code":  f["id"],
            "raiser": " ".join((f["fname"],f["lname"])),
            "area": str(f["farm_area"]),
            "updated": f["last_updated"],
            "intbio_score": str(biosec_score[0]),
            "intbio_isol_pen": getBioStr(f["intbio_isol_pen"]),
            "intbio_foot_dip": getBioStr(f["intbio_foot_dip"]),
            "intbio_waste_mgt": f["intbio_waste_mgt"],
            "intbio_disinfect_prem": getBioStr(f["intbio_disinfect_prem"]),
            "intbio_disinfect_vet_supp": getBioStr(f["intbio_disinfect_vet_supp"]),
        }
        farmsData.append(farmObject)

        ave_intbio += biosec_score[0]
    # debug(farmsData)

    # combine farm + tech lists into one list
    farmtechList = zip(farmsData, techList)

    # compute for -- ave column (intbio)
    ave_intbio = ave_intbio / len(farmsData)
    
    farmTotalAve = {
        "ave_intbio": round(ave_intbio, 2),
    }


    return render(request, 'farmstemp/rep-int-biosec.html', {"areaName": areaName, "isFiltered": isFiltered, "farmTotalAve": farmTotalAve, 'dateStart': sDate,'dateEnd': truEndDate,'areaList': areaQry,'farmtechList': farmtechList})


def extBiosecurity(request):
    # debug("TEST LOG: in extBiosecurity Report/n")

    """
    Gets current External Biosecurity record for each Farm within existing dates and all Areas due to no selected filters in dropdown.

    (1) earliest data, recent data of Farm 
    (2) all Area records
    (3) Farm details
        - farm code, raiser full name, area, technician assigned 
        - ExtBiosec fields and score
    """

    # for checking if filters were used in the displayed Report
    isFiltered = False

    # for setting Date input filters to today's date
    dateToday = datetime.now(timezone.utc)

    # (1) earliest and most recent last_updated in Farm
    dateASC = Farm.objects.only("last_updated").order_by('last_updated').first()
    dateDESC = Farm.objects.only("last_updated").order_by('-last_updated').first()

    # (2) all Area records
    areaQry = Area.objects.all()

    # Get technician name assigned per Farm
    farmQry = Farm.objects.all().prefetch_related("area", "area__tech").order_by("id")
    # debug("techQry -- " + str(farmQry.query))

    if not farmQry.exists(): # (ERROR) No External biosecurity records found.
        messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
        return render(request, 'farmstemp/rep-ext-biosec.html', {"isFiltered": isFiltered,'areaList': areaQry,'dateStart': dateToday,'dateEnd': dateToday})

    # debug("list for -- Field Technicians")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        # print(techObject["name"])
        techList.append(techObject)
    # debug(techList)    


    # (3) Farm details
    qry = Farm.objects.select_related('hog_raiser', 'area', 'extbio').annotate(
        fname=F("hog_raiser__fname"), 
        lname=F("hog_raiser__lname"), 
        farm_area = F("area__area_name"),
        extbioID = F("extbio__id"),
        extbio_bird_proof = F("extbio__bird_proof"),
        extbio_perim_fence = F("extbio__perim_fence"),
        extbio_fiveh_m_dist = F("extbio__fiveh_m_dist"),
        extbio_prvdd_foot_dip = F("extbio__prvdd_foot_dip"),
        extbio_prvdd_alco_soap = F("extbio__prvdd_alco_soap"),
        extbio_obs_no_visitors = F("extbio__obs_no_visitors"),
        extbio_prsnl_dip_footwear = F("extbio__prsnl_dip_footwear"),
        extbio_prsnl_sanit_hands = F("extbio__prsnl_sanit_hands"),
        extbio_chg_disinfect_daily = F("extbio__chg_disinfect_daily")
        ).values(
            "id",
            "fname",
            "lname", 
            "farm_area",
            "last_updated",
            "extbioID",
            "extbio_bird_proof",
            "extbio_perim_fence",
            "extbio_fiveh_m_dist",
            "extbio_prvdd_foot_dip",
            "extbio_prvdd_alco_soap",
            "extbio_obs_no_visitors",
            "extbio_prsnl_dip_footwear",
            "extbio_prsnl_sanit_hands",
            "extbio_chg_disinfect_daily"
            ).order_by("id")
    # debug(qry)

    if not qry.exists(): #(ERROR) No External biosecurity records found.
        messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
        return render(request, 'farmstemp/rep-ext-biosec.html', {"isFiltered": isFiltered,'areaList': areaQry,'dateStart': dateToday,'dateEnd': dateToday})

    farmsData = []
    ave_extbio = 0

    for f in qry:
        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], None, f["extbioID"])

        farmObject = {
            "code":  f["id"],
            "raiser": " ".join((f["fname"],f["lname"])),
            "area": str(f["farm_area"]),
            "updated": f["last_updated"],
            "extbio_score": str(biosec_score[1]),
            "extbio_bird_proof": getBioStr(f["extbio_bird_proof"]),
            "extbio_perim_fence": getBioStr(f["extbio_perim_fence"]),
            "extbio_fiveh_m_dist": getBioStr(f["extbio_fiveh_m_dist"]),
            "extbio_prvdd_foot_dip": getBioStr(f["extbio_prvdd_foot_dip"]),
            "extbio_prvdd_alco_soap": getBioStr(f["extbio_prvdd_alco_soap"]),
            "extbio_obs_no_visitors": getBioStr(f["extbio_obs_no_visitors"]),
            "extbio_prsnl_dip_footwear": getBioStr(f["extbio_prsnl_dip_footwear"]),
            "extbio_prsnl_sanit_hands": getBioStr(f["extbio_prsnl_sanit_hands"]),
            "extbio_chg_disinfect_daily": getBioStr(f["extbio_chg_disinfect_daily"]),
        }
        farmsData.append(farmObject)

        ave_extbio += biosec_score[1]

    # debug(farmsData)

    # combine farm + tech lists into one list
    farmtechList = zip(farmsData, techList)

    # compute for -- ave column (extbio)
    ave_extbio = ave_extbio / len(farmsData)
    
    farmTotalAve = {
        "ave_extbio": round(ave_extbio, 2),
    }


    return render(request, 'farmstemp/rep-ext-biosec.html', {"isFiltered": isFiltered, "farmTotalAve": farmTotalAve, 'dateStart': dateToday,'dateEnd': dateToday,'areaList': areaQry,'farmtechList': farmtechList})


def filter_extBiosec(request, startDate, endDate, areaName):
    # debug("TEST LOG: in filter_extBiosec Report/n")

    """
    Gets External Biosecurity records for each Farm based on (1) date range and (2) area name.

    (1) all Area records
    (2) Farm and Internal Biosec details
        - farm code, raiser full name, area, technician assigned 
        - ExtBiosec fields and score
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

        # Get technician name assigned per Farm
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).all().prefetch_related("area", "area__tech").order_by("id")

        if not farmQry.exists(): # (ERROR) No External biosecurity records found.
            messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
            return render(request, 'farmstemp/rep-ext-biosec.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})

        qry = Farm.objects.filter(last_updated__range=(sDate, eDate)).select_related('hog_raiser', 'area').annotate(
                fname=F("hog_raiser__fname"), 
                lname=F("hog_raiser__lname"), 
                farm_area = F("area__area_name"),
                extbioID = F("extbio__id"),
                extbio_bird_proof = F("extbio__bird_proof"),
                extbio_perim_fence = F("extbio__perim_fence"),
                extbio_fiveh_m_dist = F("extbio__fiveh_m_dist"),
                extbio_prvdd_foot_dip = F("extbio__prvdd_foot_dip"),
                extbio_prvdd_alco_soap = F("extbio__prvdd_alco_soap"),
                extbio_obs_no_visitors = F("extbio__obs_no_visitors"),
                extbio_prsnl_dip_footwear = F("extbio__prsnl_dip_footwear"),
                extbio_prsnl_sanit_hands = F("extbio__prsnl_sanit_hands"),
                extbio_chg_disinfect_daily = F("extbio__chg_disinfect_daily")
                ).values(
                    "id",
                    "fname",
                    "lname", 
                    "farm_area",
                    "last_updated",
                    "extbioID",
                    "extbio_bird_proof",
                    "extbio_perim_fence",
                    "extbio_fiveh_m_dist",
                    "extbio_prvdd_foot_dip",
                    "extbio_prvdd_alco_soap",
                    "extbio_obs_no_visitors",
                    "extbio_prsnl_dip_footwear",
                    "extbio_prsnl_sanit_hands",
                    "extbio_chg_disinfect_daily"
                    ).order_by("id")

    else: # (CASE 2) search by BOTH date range and areaName
        debug("TRACE: in else/")

        # Get technician name assigned per Farm
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).filter(area__area_name=areaName).all().prefetch_related("area", "area__tech").order_by("id")

        if not farmQry.exists(): # (ERROR) No External biosecurity records found.
            messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
            return render(request, 'farmstemp/rep-ext-biosec.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})

        qry = Farm.objects.filter(last_updated__range=(sDate, eDate)).filter(area__area_name=areaName).select_related('hog_raiser', 'area').annotate(
                fname=F("hog_raiser__fname"), 
                lname=F("hog_raiser__lname"), 
                farm_area = F("area__area_name"),
                extbioID = F("extbio__id"),
                extbio_bird_proof = F("extbio__bird_proof"),
                extbio_perim_fence = F("extbio__perim_fence"),
                extbio_fiveh_m_dist = F("extbio__fiveh_m_dist"),
                extbio_prvdd_foot_dip = F("extbio__prvdd_foot_dip"),
                extbio_prvdd_alco_soap = F("extbio__prvdd_alco_soap"),
                extbio_obs_no_visitors = F("extbio__obs_no_visitors"),
                extbio_prsnl_dip_footwear = F("extbio__prsnl_dip_footwear"),
                extbio_prsnl_sanit_hands = F("extbio__prsnl_sanit_hands"),
                extbio_chg_disinfect_daily = F("extbio__chg_disinfect_daily")
                ).values(
                    "id",
                    "fname",
                    "lname", 
                    "farm_area",
                    "last_updated",
                    "extbioID",
                    "extbio_bird_proof",
                    "extbio_perim_fence",
                    "extbio_fiveh_m_dist",
                    "extbio_prvdd_foot_dip",
                    "extbio_prvdd_alco_soap",
                    "extbio_obs_no_visitors",
                    "extbio_prsnl_dip_footwear",
                    "extbio_prsnl_sanit_hands",
                    "extbio_chg_disinfect_daily"
                    ).order_by("id")


    if not qry.exists(): # (ERROR) No External biosecurity records found.
        messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
        return render(request, 'farmstemp/rep-ext-biosec.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})
        
    # format Technician names per Farm
    # debug("list for -- Field Technicians")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        # print(techObject["name"])
        techList.append(techObject)
    # debug(techList)   

    farmsData = []
    ave_extbio = 0

    # (2) format Farm and Biosec details
    for f in qry:
        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], None, f["extbioID"])

        farmObject = {
            "code":  f["id"],
            "raiser": " ".join((f["fname"],f["lname"])),
            "area": str(f["farm_area"]),
            "updated": f["last_updated"],
            "extbio_score": str(biosec_score[1]),
            "extbio_bird_proof": getBioStr(f["extbio_bird_proof"]),
            "extbio_perim_fence": getBioStr(f["extbio_perim_fence"]),
            "extbio_fiveh_m_dist": getBioStr(f["extbio_fiveh_m_dist"]),
            "extbio_prvdd_foot_dip": getBioStr(f["extbio_prvdd_foot_dip"]),
            "extbio_prvdd_alco_soap": getBioStr(f["extbio_prvdd_alco_soap"]),
            "extbio_obs_no_visitors": getBioStr(f["extbio_obs_no_visitors"]),
            "extbio_prsnl_dip_footwear": getBioStr(f["extbio_prsnl_dip_footwear"]),
            "extbio_prsnl_sanit_hands": getBioStr(f["extbio_prsnl_sanit_hands"]),
            "extbio_chg_disinfect_daily": getBioStr(f["extbio_chg_disinfect_daily"]),
        }
        farmsData.append(farmObject)

        ave_extbio += biosec_score[1]
    # debug(farmsData)

    # combine farm + tech lists into one list
    farmtechList = zip(farmsData, techList)

    # compute for -- ave column (extbio)
    ave_extbio = ave_extbio / len(farmsData)
    
    farmTotalAve = {
        "ave_extbio": round(ave_extbio, 2),
    }

    return render(request, 'farmstemp/rep-ext-biosec.html', {"isFiltered": isFiltered,"areaName": areaName, "farmTotalAve": farmTotalAve, 'dateStart': sDate,'dateEnd': truEndDate,'areaList': areaQry,'farmtechList': farmtechList})

# FOR MANAGER DASHBOARD
def dashboard_view(request):
    """
    For rendering Farm-related statistics in dashboard.
    """

    # Get Farm details 
    farmQry = Farm.objects.select_related('intbio', 'extbio').annotate(
        intbioID = F("intbio__id"),
        extbioID = F("extbio__id"),
        last_update = F("extbio__last_updated")
        ).values(
            "id",
            "total_pigs",
            "intbioID",
            "extbioID",
            "last_update"
            ).order_by("id").all()
    # debug(farmQry)

    if not farmQry.exists(): 
        # messages.error(request, "No farm details found.", extra_tags="farm-dashboard")
        return render(request, 'dashboard.html', {})

    total_farms = 0
    total_pigs = 0
    total_needInspect = 0
    total_active = 0
    ave_intbio = 0
    ave_extbio = 0
    ave_mortRate = 0

    for f in farmQry:
        # compute int-extbio scores per Farm
        biosec_score = computeBioscore(f["id"], f["intbioID"], f["extbioID"])

        # get total pigs of all Farms
        total_pigs += f["total_pigs"]

        ave_intbio += biosec_score[0]
        ave_extbio += biosec_score[1]

        ave_mortRate += compute_MortRate(f["id"], None)

        # check if Checklist has not been updated for > 7 days
        bioDateDiff = datetime.now(timezone.utc) - f["last_update"]
        
        if bioDateDiff.days > 7 and f["total_pigs"] > 0:
            total_needInspect += 1

        # for filtering Incidents for latest Farm version
        latestPP = Pigpen_Group.objects.filter(ref_farm_id=f["id"]).order_by("-date_added").first()

        # counts no of. Incident records with "Active" status
        total_active += Hog_Symptoms.objects.filter(ref_farm_id=f["id"]).filter(pigpen_grp_id=latestPP.id).filter(report_status="Active").count()

    # debug(farmsData)

    total_farms = len(farmQry)
    # compute for -- total (pigs) and ave columns (intbio, extbio)
    ave_pigs     = round((total_pigs / len(farmQry)), 2)
    ave_intbio   = round((ave_intbio / len(farmQry)), 2)
    ave_extbio   = round((ave_extbio / len(farmQry)), 2)
    ave_mortRate = round((ave_mortRate / len(farmQry)), 2)
    

    farmStats = {
        "total_farms": total_farms,
        "total_pigs": total_pigs,
        "total_needInspect": total_needInspect,
        "total_active": total_active,
        "ave_intbio": round(ave_intbio, 2),
        "ave_extbio": round(ave_extbio, 2),
        "ave_mortRate": round(ave_mortRate, 2),
    }

    # return render(request, 'dashboard.html', {"fStats": farmStats})
    return farmStats
from django.contrib.auth.models import User
from django.db.models.expressions import F, Value
from django.db.models import Q
from django.forms.formsets import formset_factory

# for page redirection, server response
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, response

# for AJAX functions
from django.http import JsonResponse
from django.core import serializers
import json

# for Forms
from .forms import HogRaiserForm, FarmForm, PigpenMeasuresForm, InternalBiosecForm, ExternalBiosecForm, ActivityForm, AreaForm, MemAnnouncementForm

# for storing success and error Django messages
from django.contrib import messages

# for Model imports
from .models import Area, ExternalBiosec, InternalBiosec, Farm, Hog_Raiser, Pigpen_Measures, Activity, Mem_Announcement
from django.db.models.functions import Concat

#Creating a cursor object using the cursor() method
from django.shortcuts import render

# for date and time fields in Models
from datetime import date
from datetime import datetime, timezone, timedelta
from django.utils.timezone import make_aware

# for getting date today
from django.utils.timezone import now 


def debug(m):
    """
    For debugging purposes

    :param m: The message
    :type m: String
    """
    print("------------------------[DEBUG]------------------------")
    print(m)
    print("-------------------------------------------------------")

# Farms Management Module Views

## Farms table for all users except Technicians
def farms(request):
    """
    Display all farms for assistant manager
    """
    qry = Farm.objects.select_related('hog_raiser', 'area').annotate(
            fname=F("hog_raiser__fname"), 
            lname=F("hog_raiser__lname"), 
            contact=F("hog_raiser__contact_no"),
            farm_area = F("area__area_name")
            ).values(
                "id",
                "fname",
                "lname", 
                "contact", 
                "farm_address",
                "farm_area",
                "total_pigs",
                "num_pens",
                "last_updated"
                )
    debug(qry)
    farmsData = []
    for f in qry:
        farmObject = {
            "code":  str(f["id"]),
            "raiser": " ".join((f["fname"],f["lname"])),
            "contact": f["contact"],
            "address": f["farm_address"],
            "area": str(f["farm_area"]),
            "pigs": str(f["total_pigs"]),
            "pens": str(f["num_pens"]),
            "updated": f["last_updated"]
        }
        farmsData.append(farmObject)
    debug(farmsData)
    return render(request, 'farmstemp/farms.html', {"farms":farmsData}) ## Farms table for all users except Technicians

def selectedFarm(request, farmID):
    """
    Display information of selected farm for assistant manager

    :param farmID: PK of selected farm
    :type farmID: integer
    """
    qry = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'extbio', 'area').annotate(
        raiser=Concat('hog_raiser__fname', Value(' '), 'hog_raiser__lname'),
        contact=F("hog_raiser__contact_no"),
        length=F("wh_length"),
        width=F("wh_width"),
        farm_area = F("area__area_name")
    )
    context = qry.values(
        "id",
        "raiser",
        "contact",
        "directly_manage",
        "farm_address",
        "farm_area",
        "roof_height",
        "length",
        "width",
        "feed_trough",
        "bldg_cap"    
    ).first()
   
    return render(request, 'farmstemp/selected-farm.html', context)

def techFarms(request):
    """
    - Display all farms assigned to currently logged in technician. 
    - Will only display the approved farms.
    """
    
    # get all farms under the current technician 
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all()
    print("TEST LOG areaQry: " + str(areaQry))
    
        # area_num = 1
    # # concatenate all areas into one string (for frontend purposes)
    # for area in areaQry :
    #     if area_num == len(areaQry):
    #         areaList = Concat('area.area_name')
    #     else :
    #         areaList = Concat('area.area_name', Value(', '))

    #     area_num += 1

    # collect number of areas assigned (for frontend purposes)
    areaNum = len(areaQry)
    print("TEST LOG areaNum: " + str(areaNum))

    # array to store all farms under each area
    techFarmsList = []
    
    # collect all farms under each area
    for area in areaQry :
        print(str(area.id) + str(area.area_name))

        # collect the corresponding hog raiser details for each farm 
        techFarmQry  = Farm.objects.filter(area_id=area.id).select_related('hog_raiser').annotate(
                    fname=F("hog_raiser__fname"), lname=F("hog_raiser__lname"), contact=F("hog_raiser__contact_no")).values(
                            "id",
                            "fname",
                            "lname", 
                            "contact", 
                            "farm_address",
                            "last_updated")

        print("TEST LOG techFarmQry: " + str(techFarmQry))

        # pass all data into an array
        for farm in techFarmQry:
            
            farmObject = {
                "code": str(farm["id"]),
                "raiser": " ".join((farm["fname"],farm["lname"])),
                "contact": farm["contact"],
                "address": farm["farm_address"],
                "updated": farm["last_updated"],
            }

            techFarmsList.append(farmObject)
    
    # pass techFarmsList array to template
    # return render(request, 'farmstemp/tech-farms.html', { 'techFarms' : techFarmsList, 'areaCount' : areaNum, 'areaList' : areaQry, 'areas' : areaList })
    return render(request, 'farmstemp/tech-farms.html', { 'techFarms' : techFarmsList, 'areaCount' : areaNum, 'areaList' : areaQry }) 


def techSelectedFarm(request, farmID):
    """
    - Display details of the selected farm under the currently logged in technician.
    - Will collect the hog raiser, area, internal and external biosecurity, and pigpen measures connected to the farm.   
    """

    ## get details of selected farm
    # collect the corresponding details for: hog raiser, area, internal and external biosecurity
    techFarmQry = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'internalbiosec', 'externalbiosec').annotate(
                    raiser      = Concat('hog_raiser__fname', Value(' '), 'hog_raiser__lname'),
                    contact     = F("hog_raiser__contact_no"),
                    farm_area   = F("area__area_name"),
                    waste_mgt   = F("intbio__waste_mgt"),
                    isol_pen    = F("intbio__isol_pen"),
                    bird_proof  = F("extbio__bird_proof"),
                    perim_fence = F("extbio__perim_fence"),
                    foot_dip    = F("intbio__foot_dip"),
                    fiveh_m_dist = F("extbio__fiveh_m_dist"),
                    )

    # pass all data into an object
    selTechFarm = techFarmQry.values(
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
        "waste_mgt",
        "isol_pen",
        "bird_proof",
        "perim_fence",
        "foot_dip",
        "fiveh_m_dist",
    ).first()

    # collect the corresponding pigpens for selected farm
    pigpenQry = Pigpen_Measures.objects.filter(ref_farm_id=farmID).order_by('id')

    pen_no = 1
    pigpenList = []

    for pen in pigpenQry:
        pigpenObj = {
            'pen_no' : pen_no,
            'length' : pen.length,
            'width' : pen.width,
            'num_heads' : pen.num_heads
        }
        
        pigpenList.append(pigpenObj)

        pen_no += 1

    # FOR TESTING
    # print("TEST LOG pigpenQry: " + str(pigpenQry.query))
    # print("TEST LOG pigpenList: " + str(pigpenList))
    # print("TEST LOG waste_mgt: " + str(techFarmQry.values("isol_pen")))

    # pass (1) delected farm + biosecurity details, and (2) pigpen measures object to template   
    return render(request, 'farmstemp/tech-selected-farm.html', {'farm' : selTechFarm, 'pigpens' : pigpenList})

def addFarm(request):
    """
    - Redirect to Add Farm Page and render corresponding Django forms
    - Add new farm to database (will be sent for approval by asst. manager)
    - Save details to hog_raiser, farm, pigpen_measure, and externalbiosec and internalbiosec tables
    - Django forms will first check the validity of input (based on the fields within models.py)
    """
    
    # get current user (technician) ID
    techID = request.user.id

    # collect all assigned areas under technician; to be passed to template
    areaQry = Area.objects.filter(tech_id=techID)
    # print("TEST LOG areaQry: " + str(areaQry))

    if request.method == 'POST':
        print("TEST LOG: Form has POST method") 
        print(request.POST)

        # collect non-Django form inputs
        farmID = request.POST.get("input-code", None)
        # print("TEST LOG farmID: " + farmID)

        areaName = request.POST.get("input-area", None)
        # print("TEST LOG areaName: " + areaName)

        # get ID of selected area
        areaIDQry = Area.objects.filter(area_name=areaName).first()
        # print("TEST LOG areaIDQry: " + str(areaIDQry))

        areaID = areaIDQry.id
        print("TEST LOG areaID: " + str(areaID))

        # render forms
        hogRaiserForm       = HogRaiserForm(request.POST)
        farmForm            = FarmForm(request.POST)
        pigpenMeasuresForm  = PigpenMeasuresForm(request.POST)

        # if request.POST.get("bird_proof") == 'on':
        #     request.POST.update("bird_proof", 1)
        # else :
        #     request.POST.update("bird_proof")

        # if request.POST.get("perim_fence") == 'on':
        #     request.POST.update("perim_fence")
        # else :
        #     request.POST.update("perim_fence")

        # if request.POST.get("fiveh_m_dist") == 'on':
        #     request.POST.update("fiveh_m_dist")
        # else :
        #     request.POST.update("fiveh_m_dist")

        # data = request.POST.copy()
        # if data['bird_proof'] == 'on' : 
        #     data['bird_proof'] = 0
        # else :
        #     data['bird_proof'] = 1

        # request.POST = data

        # print("TEST LOG externalBiosecForm: " + str(request.POST.get("bird_proof")))
    
        externalBiosecForm  = ExternalBiosecForm(request.POST)
        internalBiosecForm  = InternalBiosecForm(request.POST)

        if hogRaiserForm.is_valid():
            hogRaiser = hogRaiserForm.save(commit=False)
            hogRaiser.save()

            print("TEST LOG: Added new raiser")

            if externalBiosecForm.is_valid():
                externalBiosec = externalBiosecForm.save(commit=False)

                # if externalBiosec.bird_proof == 'on':
                #     externalBiosec.bird_proof == 0
                # else :
                #     externalBiosec.bird_proof == 1

                # if externalBiosec.perim_fence == 'on':
                #     externalBiosec.perim_fence== 0
                # else :
                #     externalBiosec.perim_fence == 1

                # if externalBiosec.fiveh_m_dist == 'on':
                #     externalBiosec.fiveh_m_dist == 0
                # else :
                #     externalBiosec.fiveh_m_dist == 1

                # print("TEST LOG externalBiosec.bird_proof: " + str(externalBiosec.bird_proof))
                # print("TEST LOG externalBiosec.perim_fence: " + str(externalBiosec.perim_fence))
                # print("TEST LOG externalBiosec.fiveh_m_dist: " + str(externalBiosec.fiveh_m_dist))

                externalBiosec.save()
                print("TEST LOG: Added new external biosec")

                if internalBiosecForm.is_valid():
                    internalBiosec = internalBiosecForm.save(commit=False)

                    internalBiosec.save()
                    print("TEST LOG: Added new internal biosec")
                    
                    if farmForm.is_valid():
                        farm = farmForm.save(commit=False)

                        farm.hog_raiser_id = hogRaiser.id
                        farm.extbio_id = externalBiosec.id
                        farm.intbio_id = internalBiosec.id
                        farm.area_id = areaID
                        farm.id = farmID

                        # print("TEST LOG farm.area_id: " + str(farm.area_id))

                        farm.save()
                        print("TEST LOG: Added new farm")

                        # get recently created internal and external biosec IDs and update ref_farm_id
                        externalBiosec.ref_farm_id = farm
                        internalBiosec.ref_farm_id = farm

                        externalBiosec.save()
                        internalBiosec.save()

                        if pigpenMeasuresForm.is_valid():
                            pigpenMeasures = pigpenMeasuresForm.save(commit=False)

                            # for num_heads in request.POST.get("num_heads") :
                            #     pigpenMeasures = pigpenMeasuresForm.save(commit=False)

                            #     pigpenMeasures.ref_farm_id = farm.id

                            #     print(str(pigpenMeasures.length))
                            
                            pigpenMeasures.save()
                            print("TEST LOG: Added new pigpen measure")

                            # add all num_heads (pigpen measure) for total_pigs (farm)


                            # update total_pigs of newly added farm

                            # temporary
                            farm.total_pigs = pigpenMeasures.num_heads
                            farm.save()
                            
                            # print("TEST LOG pigpenMeasures.num_heads: " + str(pigpenMeasures.num_heads))
                            # print("TEST LOG farm.total_pigs: " + str(farm.total_pigs))

                            return render(request, 'home.html', {})

                        else:
                            print("TEST LOG: Pigpen Measures Form not valid")
                            print(pigpenMeasuresForm.errors)
                    
                    else:
                        print("TEST LOG: Farm Form not valid")
                        print(farmForm.errors)

                else:
                    print("TEST LOG: Internal Biosec Form not valid")
                    print(internalBiosecForm.errors)

            else:
                print("TEST LOG: External Biosec Form not valid")
                print(externalBiosecForm.errors)
            
        else:
            print("TEST LOG: Hog Raiser Form not valid")
            print(hogRaiserForm.errors)
     
    else:
        print("TEST LOG: Form is not a POST method")

        # if the forms have no input yet, only display empty forms
        hogRaiserForm       = HogRaiserForm()
        farmForm            = FarmForm()
        pigpenMeasuresForm  = PigpenMeasuresForm()
        externalBiosecForm  = ExternalBiosecForm()
        internalBiosecForm  = InternalBiosecForm()

    # pass django forms to template
    return render(request, 'farmstemp/add-farm.html', { 'area' : areaQry,
                                                        'hogRaiserForm' : hogRaiserForm,
                                                        'farmForm' : farmForm,
                                                        'pigpenMeasuresForm' : pigpenMeasuresForm,
                                                        'externalBiosecForm' : externalBiosecForm,
                                                        'internalBiosecForm' : internalBiosecForm})
 

# (POST-AJAX) For searching a Biosec Checklist based on biosecID; called in AJAX request
def search_bioChecklist(request, biosecID):
    """
    (POST-AJAX) For searching a Biosecurity Checklist based on biosecID.
    """

    if request.is_ajax and request.method == 'POST':

        print("TEST LOG: in search_bioChecklist()")

        # Get biosecID passed from AJAX URL param 
        bioID = biosecID 

        if bioID is None:
            # (ERROR) Invalid or null biosecID
            debug("(ERROR) Invalid or null biosecID")
            # messages.error(request, "Invalid biosecurity ID.", extra_tags='search-checklist')
            return JsonResponse({"error": "Invalid biosecurity ID."}, status=400)
            
        else:
            debug("in search_bioChecklist(): bioID -- " + str(bioID))

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

            if ext.exists() and inter.exists():
                # Get first instance in biosec queries
                ext = ext.first()
                inter = inter.first()

                # Format int-ext biosec fields in a dictionary
                bioDict = {
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

    if request.is_ajax and request.method == 'POST':

        print("TEST LOG: in update_bioChecklist()/n")

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
                    extDateDiff = datetime.now(timezone.utc) - intBio.last_updated
                    intDateDiff = datetime.now(timezone.utc) - intBio.last_updated
                    
                    debug("extDateDiff.days" + str(extDateDiff.days))
                    debug("intDateDiff" + str(intDateDiff.days))

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

# (POST) function for adding a Biosec Checklist
def post_addChecklist(request, farmID):
    print("TEST LOG: in post_addChecklist/n")

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

            debug("TEST LOG: List of Biocheck values")
            for index, value in enumerate(biosecArr): 
                if value is None:
                    # (ERROR) Incomplete input/s for Biosecurity Checklist
                    debug("ERROR: Index value in biosec is None.")
                    checkComplete = False

                    messages.error(request, "Incomplete input/s for Biosecurity Checklist.", extra_tags='add-checklist')
                    return redirect('/add-checklist/' + farmID)

                # int(value)
                # print(list((index, value)))

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

                debug("BIOMEASURE: -- " + str(bioMeasure))

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
                df = ts.strftime("%m/%d/%Y, %H:%M")
                debug(extBio.last_updated)
                
                # (SUCCESS) Biochecklist has been added. Properly redirect to Biosec main page
                messages.success(request, "Checklist made on " + df + " has been successfully added!", extra_tags='add-checklist')
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

def delete_bioChecklist(request, biosecID, farmID):
    """
    (POST-AJAX) For deleting a biosecurity checklist based on biosecID and farmID from dropdowns.
        Handles two scenarios:
        - (1) To be deleted Checklist is current Biosec in Farm
        - (2) Not current checklist in Farm, simply delete record
    """

    if request.is_ajax and request.method == 'POST':

        print("TEST LOG: in delete_bioChecklist()/n")

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

# For getting all Biosec checklist versions under a Farm.
def biosec_view(request):
    """
    For getting all Biosecurity details under a Farm. 
    This function gets the ID of the first Farm due to no passed farmID as parameter.

    - (1) farms under Technician user, 
    - (2) latest intbio-extbio Checklist, 
    - (3) all biosec IDs and dates within that Farm, 
    - (4) activities
    """

    print("TEST LOG: in Biosec view/n")

    # (1) Get all Farms under the logged-in technician User
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all()
    print("TEST LOG areaQry: " + str(areaQry))

    # array to store all farms under each area
    techFarmsList = []

    for area in areaQry :
        print(str(area.id) + str(area.area_name))

        # collect the corresponding hog raiser details for each farm 
        techFarmQry  = Farm.objects.filter(area_id=area.id).values(
            "id"
        ).all()
        debug("techFarmQry -- " + str(techFarmQry))

        # pass all data into an array
        for farm in techFarmQry:
            farmObject = {
                "id": str(farm["id"]),
            }
            techFarmsList.append(farmObject)

    debug("techFarmsList -- " + str(techFarmsList))


    # (ERROR) for checking technician Areas that have no Farms and null farmID
    if not techFarmsList: 
        messages.error(request, "Farm record/s not found.", extra_tags="view-biosec")
        return render(request, 'farmstemp/biosecurity.html', {})
    else: 

        # Get ID of first farm under technician
        firstFarm = str(*techFarmsList[0].values())
        farmID = int(firstFarm)

        debug("biosec_view() farmID -- " + str(farmID))

        
        # Get current internal and external FKs
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


        # print("TEST LOG biosec_view(): Queryset external-- " + str(extQuery.query))
        print("TEST LOG currbioQuery len(): " + str(len(currbioQuery)))


        # (4) GET ACTIVITIES
        actQuery = Activity.objects.filter(ref_farm_id=farmID).filter(is_approved=True).all().order_by('-date')

        actList = []

        # store all data to an array
        for activity in actQuery:
            actList.append({
                'date' : activity.date,
                'trip_type' : activity.trip_type,
                'time_departure' : activity.time_departure,
                'time_arrival' : activity.time_arrival,
                'description' : activity.description,
                'remarks' : activity.remarks,
                # 'last_updated' : last_updated,
            })

        # pass in context:
        # - (1) farmIDs under Technician user, 
        # - (2) latest intbio-extbio Checklist, 
        # - (3) all biocheck IDs and dates within that Farm, 
        # - (4) activities
        return render(request, 'farmstemp/biosecurity.html', {'farmID' : farmID, 'farmList': techFarmsList,'currBio': currbioObj, 'bioList': extQuery, 'activity' : actList}) 
    
    return render(request, 'farmstemp/biosecurity.html', {}) 

# For getting all Biosec checklist versions under a Farm based on farmID.
def select_biosec(request, farmID):
    """
    For getting all Biosecurity details under a Farm. 
    This serves as a search function when a farmID or farm code is selected from its dropdown.

    - (1) farms under Technician user, 
    - (2) latest intbio-extbio Checklist, 
    - (3) all biosec IDs and dates within that Farm, 
    - (4) activities
    """

    print("TEST LOG: in Biosec view/n")

    # # (1) Get all Farms under the logged-in technician User
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all()
    print("TEST LOG areaQry: " + str(areaQry))

    # array to store all farms under each area
    techFarmsList = []

    for area in areaQry :
        print(str(area.id) + str(area.area_name))

        # collect the corresponding hog raiser details for each farm 
        techFarmQry  = Farm.objects.filter(area_id=area.id).values(
            "id"
        ).all()
        debug("techFarmQry -- " + str(techFarmQry))

        # pass all data into an array
        for farm in techFarmQry:
            farmObject = {
                "id": str(farm["id"]),
            }
            techFarmsList.append(farmObject)

    debug("techFarmsList -- " + str(techFarmsList))

    # Get farmID passed from URL param
    farmID = farmID
    debug("in select_biosec() farmID -- " + str(farmID))

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

        # print("TEST LOG biosec_view(): Queryset external-- " + str(extQuery.query))
        print("TEST LOG currbioQuery len(): " + str(len(currbioQuery)))

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
                'date' : activity.date,
                'trip_type' : activity.trip_type,
                'time_departure' : activity.time_departure,
                'time_arrival' : activity.time_arrival,
                'description' : activity.description,
                'remarks' : activity.remarks,
                # 'last_updated' : last_updated,
            })

        # pass in context:
        # - (1) farmIDs under Technician user, 
        # - (2) latest intbio-extbio Checklist, 
        # - (3) all biocheck IDs and dates within that Farm, 
        # - (4) activities
        return render(request, 'farmstemp/biosecurity.html', {'farmID' : farmID, 'farmList': techFarmsList,'currBio': currbioObj, 'bioList': extQuery, 'activity' : actList}) 

    return render(request, 'farmstemp/biosecurity.html', {}) 

def addChecklist_view(request, farmID):
    """
    For passing farmID from Biosecurity page to addChecklist page ("add-checklist.html")
    """

    debug("TEST LOG: in addChecklist_view/n")

    farm_id = farmID
    debug("TEST LOG: farm_id -- " + str(farm_id))

    return render(request, 'farmstemp/add-checklist.html', { 'farmID' : farm_id })

def techAssignment(request):
    areasData = []
    areas = Area.objects.select_related("tech_id").annotate(
        curr_tech = Concat('tech_id__first_name', Value(' '), 'tech_id__last_name')
    ).order_by('id').values()
    techs = User.objects.filter(groups__name="Field Technician").annotate(
        name = Concat('first_name', Value(' '), 'last_name'),
    ).values(
        "id",
        "name",
    )
    for a in areas:
        areaObject = {
            "id": str(a["id"]),
            "area_name": a["area_name"],
            "curr_tech_id": a["tech_id"],
            "curr_tech": a["curr_tech"],
            "farm_count": Farm.objects.filter(area=a["id"]).count()
        }
        areasData.append(areaObject)
    context = {
        "areasData":areasData,
        "technicians":techs
    }
    return render(request, 'farmstemp/assignment.html', context)

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
    debug(area.get())
    if(area.exists() and technician.exists()):
        # save changes
        a = area.get()
        a.tech_id = technician.get()
        a.save()
        debug(area.get())
        # return output
        return HttpResponse("message",status=200)
    else:
        # abort
        # return output
        return HttpResponseNotFound("Not Found",status=400)
    
    

def formsApproval(request):
    return render(request, 'farmstemp/forms-approval.html', {})

def selectedForm(request):
    return render(request, 'farmstemp/selected-form.html', {})


def addActivity(request, farmID):
    """
    - Redirect to Add Activity Page and render corresponding Django form
    - Add new activity to database (will be sent for approval by asst. manager)
    - Save details to activity and current farm tables
    """

    # collected farmID of selected tech farm
    farmID = farmID

    if request.method == 'POST':
        print("TEST LOG: Form has POST method") 
        print(request.POST)

        activityForm = ActivityForm(request.POST)

        if activityForm.is_valid():
            activity = activityForm.save(commit=False)

            activity.ref_farm_id = farmID

            activity.save()

            print("TEST LOG: Added new activty")
            return redirect('/biosecurity/' + str(farmID))
        
        else:
            print("TEST LOG: activityForm is not valid")
            print(activityForm.errors)

    else:
        print("TEST LOG: Form is not a POST method")

        # if form has no input yet, only display an empty form
        activityForm = ActivityForm()
    
    # pass django form and farmID to template
    return render(request, 'farmstemp/add-activity.html', { 'activityForm' : activityForm, 'farmID' : farmID })

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
        "name"
    )
    context = {
        "approved": announcements.filter(is_approved = True),
        "unapproved": announcements.filter(is_approved = False),
    }
    return render(request, 'farmstemp/mem-announce.html', context)

def createAnnouncement(request):
    """
    Create announcment
    Defaults to approved if assistant manager
    """
    if request.method == 'POST':
        debug(request.POST)
        debug(MemAnnouncementForm(request.POST))

    announcementForm = MemAnnouncementForm()
    return render(request, 'farmstemp/create-announcement.html', {'announcementForm' : announcementForm})

def viewAnnouncement(request):
    return render(request, 'farmstemp/view-announcement.html', {})

# helper functions for Biosec
def computeBioscore(farmID, intbioID, extbioID):
    """
    For calculating Internal and External biosec scores of a Farm.
    
    BIOSCORE = ( (total measure points + total checklist points) / (total points - N/A))
    """

    debug("in computeIntBio()/n")

    debug("param // farmID -- " + str(farmID))
    debug("param // intbioID -- " + str(intbioID))
    debug("param // extbioID -- " + str(extbioID))

    intbio_score = 0
    extbio_score = 0

# -------
    total_measures = 0
    total_checks = 0
    total_NA = 0

    # (1) INTERNAL BIOSEC SCORE
    if intbioID is None: # (ERROR) no intbioID passed
        debug("(ERROR) intbioID is null.")
    else:
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
            else:
                total_NA += 2

        # debug("intbio // total_measures -- " + str(total_measures))
        # debug("intbio // total_checks -- " + str(total_checks))
        # debug("intbio // total_NA -- " + str(total_NA))

        # compute BIOSCORE and round up to 2 decimal places
        intbio_score = ((total_measures + total_checks) / (7 - total_NA)) * 100
        intbio_score = round(intbio_score,2)
        debug("INTBIO_SCORE -- " + str(intbio_score))


# --------
    # (2) EXTERNAL BIOSEC SCORE
    if extbioID is None: # (ERROR) no extbioID passed
        debug("(ERROR) extbioID is null.")
    else:

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
        debug("EXTBIO_SCORE -- " + str(extbio_score))

    # returns a tuple; access using "var_name[0]" and "var_name[1]"
    return intbio_score, extbio_score


# REPORTS for Module 1

def farmsAssessment(request):
    debug("TEST LOG: in farmsAssessment Report/n")

    """
    Gets all Farm records within existing dates and all Areas due to no selected filters in dropdown

    (1) earliest data, recent data of Farm 
    (2) all Area records
    (3) Farm details
        - farm code, raiser full name, address, technician assigned, num pigs, num pens, 
        - intbio score, extbio score, last_updated (in Farm/Biosec?)
    """
    # (1) earliest and most recent last_updated in Farm
    dateASC = Farm.objects.only("last_updated").order_by('last_updated').first()
    dateDESC = Farm.objects.only("last_updated").order_by('-last_updated').first()

    # (2) all Area records
    areaQry = Area.objects.all()

    # Get technician name assigned per Farm
    # Farm > Area > User (tech)
    farmQry = Farm.objects.all().prefetch_related("area", "area__tech")
    debug("techQry -- " + str(farmQry.query))

    if not farmQry.exists(): # (ERROR) No farm records found.
        messages.error(request, "No farm records found.", extra_tags="farmass-report")
        return render(request, 'farmstemp/rep-farms-assessment.html', {})

    debug("list for -- Farm > Area > User (tech)")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        print(techObject["name"])
        techList.append(techObject)
    debug(techList)    


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
            )
    debug(qry)

    if not qry.exists(): 
        messages.error(request, "No farm records found.", extra_tags="farmass-report")
        return render(request, 'farmstemp/rep-farms-assessment.html', {})

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
            "code":  str(f["id"]),
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
    ave_pigs = total_pigs / len(farmsData)
    ave_pens = total_pens / len(farmsData)
    ave_intbio = ave_intbio / len(farmsData)
    ave_extbio = ave_extbio / len(farmsData)
    
    farmTotalAve = {
        "total_pigs": total_pigs,
        "total_pens": total_pens,
        "ave_pigs": ave_pigs,
        "ave_pens": ave_pens,
        "ave_intbio": round(ave_intbio, 2),
        "ave_extbio": round(ave_extbio, 2),
    }

    return render(request, 'farmstemp/rep-farms-assessment.html', {"farmTotalAve": farmTotalAve, 'dateStart': dateASC.last_updated,'dateEnd': dateDESC.last_updated,'areaList': areaQry,'farmtechList': farmtechList})


def filter_farmsAssessment(request, startDate, endDate, areaName):
    """
    Gets Farm records based on (1) date range and (2) area name filters.

    (1) earliest data, recent data of Farm 
    (2) Area selected in dropdown (?)
    (3) Farm details
        - farm code, raiser full name, address, technician assigned, num pigs, num pens, 
        - intbio score, extbio score, last_updated (in Farm/Biosec?)
    """

    debug("TEST LOG: in filter_farmsAssessment Report()/n")

    debug("URL params:")
    debug("startDate -- " + startDate)
    debug("endDate -- " + endDate)
    debug("areaName -- " + areaName)


    # convert str Dates to date type; then to a timezone-aware datetime
    sDate = make_aware(datetime.strptime(startDate, "%Y-%m-%d")) 
    eDate = make_aware(datetime.strptime(endDate, "%Y-%m-%d")) + timedelta(1) # add 1 day to endDate

    debug("converted sDate -- " + str(type(sDate)))
    debug("converted eDate -- " + str(type(eDate)))


    # (2) all Area records for dropdown
    areaQry = Area.objects.all()


    # (3) Farm details based on selected filters
    if areaName == "All": # (CASE 1) search only by date range
        debug("TRACE: in areaName == 'All'")

        # Get technician name assigned per Farm
        # Farm > Area > User (tech)
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).all().prefetch_related("area", "area__tech")

        if not farmQry.exists(): # (ERROR) No farm records found.
            messages.error(request, "No farm records found.", extra_tags="farmass-report")
            return render(request, 'farmstemp/rep-farms-assessment.html', {})

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
                )
    else: # (CASE 2) search by BOTH date range and areaName
        debug("TRACE: in else/")

        # Get technician name assigned per Farm
        # Farm > Area > User (tech)
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).filter(area__area_name=areaName).all().prefetch_related("area", "area__tech")

        if not farmQry.exists(): # (ERROR) No farm records found.
            messages.error(request, "No farm records found.", extra_tags="farmass-report")
            return render(request, 'farmstemp/rep-farms-assessment.html', {})

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
                )
   
    debug(qry)

    if not qry.exists(): 
        messages.error(request, "No farm records found.", extra_tags="farmass-report")
        return render(request, 'farmstemp/rep-farms-assessment.html', {})

    debug("list for -- Farm > Area > User (tech)")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        print(techObject["name"])
        techList.append(techObject)
    debug(techList)  

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
            "code":  str(f["id"]),
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
    ave_pigs = total_pigs / len(farmsData)
    ave_pens = total_pens / len(farmsData)
    ave_intbio = ave_intbio / len(farmsData)
    ave_extbio = ave_extbio / len(farmsData)
    
    farmTotalAve = {
        "total_pigs": total_pigs,
        "total_pens": total_pens,
        "ave_pigs": ave_pigs,
        "ave_pens": ave_pens,
        "ave_intbio": round(ave_intbio, 2),
        "ave_extbio": round(ave_extbio, 2),
    }

    # to revert endDate to same user date input
    truEndDate = eDate - timedelta(1)

    return render(request, 'farmstemp/rep-farms-assessment.html', {"farmTotalAve": farmTotalAve,'dateStart': sDate,'dateEnd': truEndDate,'areaList': areaQry,'farmtechList': farmtechList})


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
    debug("TEST LOG: in intBiosecurity Report/n")

    """
    Gets current Internal Biosecurity record for each Farm within existing dates and all Areas due to no selected filters in dropdown.

    (1) earliest data, recent data of Farm 
    (2) all Area records
    (3) Farm details
        - farm code, raiser full name, area, technician assigned 
        - (IntBiosec) isol_pen, foot_dip, waste_mgt, disinfect_prem, disinfect_vet_supp, last_updated
        - IntBiosec score
    """

    # (1) earliest and most recent last_updated in Farm
    dateASC = Farm.objects.only("last_updated").order_by('last_updated').first()
    dateDESC = Farm.objects.only("last_updated").order_by('-last_updated').first()

    # (2) all Area records
    areaQry = Area.objects.all()

    # Get technician name assigned per Farm
    farmQry = Farm.objects.all().prefetch_related("area", "area__tech")
    # debug("techQry -- " + str(farmQry.query))

    if not farmQry.exists(): # (ERROR) No Internal biosecurity records found.
        messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
        return render(request, 'farmstemp/rep-int-biosec.html', {})

    debug("list for -- Field Technicians")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        print(techObject["name"])
        techList.append(techObject)
    debug(techList)    


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
            )
    debug(qry)

    if not qry.exists(): #(ERROR) No Internal biosecurity records found.
        messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
        return render(request, 'farmstemp/rep-int-biosec.html', {})

    farmsData = []
    ave_intbio = 0

    for f in qry:

        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], f["intbioID"], None)

        farmObject = {
            "code":  str(f["id"]),
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

    return render(request, 'farmstemp/rep-int-biosec.html', {"farmTotalAve": farmTotalAve, 'dateStart': dateASC.last_updated,'dateEnd': dateDESC.last_updated,'areaList': areaQry,'farmtechList': farmtechList})


def filter_intBiosec(request, startDate, endDate, areaName):
    debug("TEST LOG: in filter_intBiosec Report/n")

    """
    Gets Internal Biosecurity records for each Farm based on (1) date range and (2) area name.

    (1) all Area records
    (2) Farm and Internal Biosec details
        - farm code, raiser full name, area, technician assigned 
        - (IntBiosec) isol_pen, foot_dip, waste_mgt, disinfect_prem, disinfect_vet_supp, last_updated
        - IntBiosec score
    """

    debug("URL params:")
    debug("startDate -- " + startDate)
    debug("endDate -- " + endDate)
    debug("areaName -- " + areaName)


    # convert str Dates to date type; then to a timezone-aware datetime
    sDate = make_aware(datetime.strptime(startDate, "%Y-%m-%d")) 
    eDate = make_aware(datetime.strptime(endDate, "%Y-%m-%d")) + timedelta(1) # add 1 day to endDate

    debug("converted sDate -- " + str(type(sDate)))
    debug("converted eDate -- " + str(type(eDate)))


    # (1) all Area records
    areaQry = Area.objects.all()

    if areaName == "All": # (CASE 1) search only by date range
        debug("TRACE: in areaName == 'All'")

        # Get technician name assigned per Farm
        # Farm > Area > User (tech)
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).all().prefetch_related("area", "area__tech")

        if not farmQry.exists(): # (ERROR) No Internal biosecurity records found.
            messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
            return render(request, 'farmstemp/rep-int-biosec.html', {})


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
                    )

    else: # (CASE 2) search by BOTH date range and areaName
        debug("TRACE: in else/")

        # Get technician name assigned per Farm
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).filter(area__area_name=areaName).all().prefetch_related("area", "area__tech")

        if not farmQry.exists(): # (ERROR) No Internal biosecurity records found.
            messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
            return render(request, 'farmstemp/rep-int-biosec.html', {})

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
                )


    if not qry.exists(): # (ERROR) No Internal biosecurity records found.
        messages.error(request, "No Internal biosecurity records found.", extra_tags="intbio-report")
        return render(request, 'farmstemp/rep-int-biosec.html', {})
        
    # format Technician names per Farm
    debug("list for -- Field Technicians")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        print(techObject["name"])
        techList.append(techObject)
    debug(techList)   

    farmsData = []
    ave_intbio = 0

    # (2) format Farm and Biosec details
    for f in qry:
        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], f["intbioID"], None)

        farmObject = {
            "code":  str(f["id"]),
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

    # to revert endDate to same user date input
    truEndDate = eDate - timedelta(1)

    return render(request, 'farmstemp/rep-int-biosec.html', {"farmTotalAve": farmTotalAve, 'dateStart': sDate,'dateEnd': truEndDate,'areaList': areaQry,'farmtechList': farmtechList})


def extBiosecurity(request):
    debug("TEST LOG: in extBiosecurity Report/n")

    """
    Gets current External Biosecurity record for each Farm within existing dates and all Areas due to no selected filters in dropdown.

    (1) earliest data, recent data of Farm 
    (2) all Area records
    (3) Farm details
        - farm code, raiser full name, area, technician assigned 
        - ExtBiosec fields and score
    """

    # (1) earliest and most recent last_updated in Farm
    dateASC = Farm.objects.only("last_updated").order_by('last_updated').first()
    dateDESC = Farm.objects.only("last_updated").order_by('-last_updated').first()

    # (2) all Area records
    areaQry = Area.objects.all()

    # Get technician name assigned per Farm
    farmQry = Farm.objects.all().prefetch_related("area", "area__tech")
    # debug("techQry -- " + str(farmQry.query))

    if not farmQry.exists(): # (ERROR) No External biosecurity records found.
        messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
        return render(request, 'farmstemp/rep-ext-biosec.html', {})

    debug("list for -- Field Technicians")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        print(techObject["name"])
        techList.append(techObject)
    debug(techList)    


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
            )
    debug(qry)

    if not qry.exists(): #(ERROR) No External biosecurity records found.
        messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
        return render(request, 'farmstemp/rep-ext-biosec.html', {})

    farmsData = []
    ave_extbio = 0

    for f in qry:
        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], None, f["extbioID"])

        farmObject = {
            "code":  str(f["id"]),
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

    return render(request, 'farmstemp/rep-ext-biosec.html', {"farmTotalAve": farmTotalAve, 'dateStart': dateASC.last_updated,'dateEnd': dateDESC.last_updated,'areaList': areaQry,'farmtechList': farmtechList})


def filter_extBiosec(request, startDate, endDate, areaName):
    debug("TEST LOG: in filter_extBiosec Report/n")

    """
    Gets External Biosecurity records for each Farm based on (1) date range and (2) area name.

    (1) all Area records
    (2) Farm and Internal Biosec details
        - farm code, raiser full name, area, technician assigned 
        - ExtBiosec fields and score
    """

    debug("URL params:")
    debug("startDate -- " + startDate)
    debug("endDate -- " + endDate)
    debug("areaName -- " + areaName)


    # convert str Dates to date type; then to a timezone-aware datetime
    sDate = make_aware(datetime.strptime(startDate, "%Y-%m-%d")) 
    eDate = make_aware(datetime.strptime(endDate, "%Y-%m-%d")) + timedelta(1) # add 1 day to endDate

    debug("converted sDate -- " + str(type(sDate)))
    debug("converted eDate -- " + str(type(eDate)))


    # (1) all Area records
    areaQry = Area.objects.all()

    if areaName == "All": # (CASE 1) search only by date range
        debug("TRACE: in areaName == 'All'")

        # Get technician name assigned per Farm
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).all().prefetch_related("area", "area__tech")

        if not farmQry.exists(): # (ERROR) No External biosecurity records found.
            messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
            return render(request, 'farmstemp/rep-ext-biosec.html', {})

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
                    )

    else: # (CASE 2) search by BOTH date range and areaName
        debug("TRACE: in else/")

        # Get technician name assigned per Farm
        farmQry = Farm.objects.filter(last_updated__range=(sDate, eDate)).filter(area__area_name=areaName).all().prefetch_related("area", "area__tech")

        if not farmQry.exists(): # (ERROR) No External biosecurity records found.
            messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
            return render(request, 'farmstemp/rep-ext-biosec.html', {})

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
                    )


    if not qry.exists(): # (ERROR) No External biosecurity records found.
        messages.error(request, "No External biosecurity records found.", extra_tags="extbio-report")
        return render(request, 'farmstemp/rep-ext-biosec.html', {})
        
    # format Technician names per Farm
    debug("list for -- Field Technicians")
    techList = []
    for f in farmQry:
        techObject = {
            "name": " ".join((f.area.tech.first_name,f.area.tech.last_name)) 
        }
        print(techObject["name"])
        techList.append(techObject)
    debug(techList)   

    farmsData = []
    ave_extbio = 0

    # (2) format Farm and Biosec details
    for f in qry:
        # compute int-extbio scores
        biosec_score = computeBioscore(f["id"], None, f["extbioID"])

        farmObject = {
            "code":  str(f["id"]),
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

    # to revert endDate to same user date input
    truEndDate = eDate - timedelta(1)

    return render(request, 'farmstemp/rep-ext-biosec.html', {"farmTotalAve": farmTotalAve, 'dateStart': sDate,'dateEnd': truEndDate,'areaList': areaQry,'farmtechList': farmtechList})

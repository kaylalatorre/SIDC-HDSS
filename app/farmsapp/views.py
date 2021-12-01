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
from .forms import HogRaiserForm, FarmForm, PigpenMeasuresForm, InternalBiosecForm, ExternalBiosecForm, ActivityForm, AreaForm
from django.forms import formset_factory

# for storing error messages
from django.contrib import messages

# for Model imports
import psycopg2
from .models import Area, ExternalBiosec, InternalBiosec, Farm, Hog_Raiser, Pigpen_Measures, Activity
from django.db.models.functions import Concat

#Creating a cursor object using the cursor() method
from django.shortcuts import render

from datetime import date

# for getting date today
from django.utils.timezone import now
from django.utils.timezone import localtime 

def debug(m):
    """
    For debugging purposes

    :param m: The message
    :type m: String
    """
    print("------------------------[DEBUG]------------------------")
    print(m)
    print("-------------------------------------------------------")

# class ActivityFormView(View):
#     # create a formset out of ActivityForm
#     Activity_FormSet = formset_factory(ActivityForm)

#     # render template were it will be displayed
#     template_name = "add-activity.html"

#     def get(self, request, *args, **kwargs):
#         # create an instance of formset and put in context dict
#         context = {
#             'activityForm' : self.Activity_FormSet(),
#         }

#         return render(request, self.template_name, context)


# Farms Management Module Views

## Farms table for all users except Technicians
def farms(request):
    
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
    # this_form = Form_DisplayFarm()
    # Form_DisplayFarm.data
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
    - Display all farms under areas assigned to currently logged in technician. 
    """
    
    # get all farms under the current technician 
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all()
    # print("TEST LOG areaQry: " + str(areaQry))
    
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
                            # "last_updated").order_by('-last_updated')

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

    farmID - selected farmID passed as parameter
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
                    fiveh_m_dist = F("extbio__fiveh_m_dist"))

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
    - Add new farm to database 
    - Save details to hog_raiser, pigpen_measure, and externalbiosec and internalbiosec tables
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
        internalBiosecForm  = InternalBiosecForm(request.POST)

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

        if hogRaiserForm.is_valid():
            hogRaiser = hogRaiserForm.save(commit=False)
            hogRaiser.save()

            print("TEST LOG: Added new raiser")

            if internalBiosecForm.is_valid():
                
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
                    waste_mgt = request.POST.get("waste_mgt", None)
                )

                print(str(internalBiosec))
        
                internalBiosec.save()
                print("TEST LOG: Added new internal biosec")
                

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

                print(str(externalBiosec))

                externalBiosec.save()
                print("TEST LOG: Added new internal biosec")
                
                if farmForm.is_valid():
                    farm = farmForm.save(commit=False)

                    # pass data as FKs for farm
                    farm.hog_raiser = hogRaiser
                    farm.extbio = externalBiosec
                    farm.intbio = internalBiosec
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
                        
                        # temporary variable to store total of all num_heads
                        numTotal = 0 
                
                        # pass all pigpenList objects into Pigpen_Measures model
                        x = 0
                        
                        for pigpen in pigpenList:
                            pigpen = pigpenList[x]
                            print("TEST LOG Pigpen " + str(x) + ": " + str(pigpenList[x]))

                            # create new instance of Pigpen_Measures model
                            pigpen_measure = Pigpen_Measures.objects.create(
                                ref_farm = farm,
                                length = pigpen['length'],
                                width = pigpen['width'],
                                num_heads = pigpen['num_heads'],
                            )
                            
                            # add all num_heads (pigpen measure) for total_pigs (farm)
                            numTotal += int(pigpen_measure.num_heads)

                            print(str(pigpen_measure))

                            pigpen_measure.save()
                            print("TEST LOG: Added new pigpen measure")

                            x += 1
                        

                        # update total_pigs of newly added farm
                        farm.total_pigs = numTotal
                        farm.save()
                        
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

                    # Format biosec fields in a dict
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
                    return JsonResponse({"instance": jsonStr}, status=200)

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
                    return redirect('/biosecurity/' + farmID)

                int(value)
                print(list((index, value)))

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

                # (SUCCESS) Biochecklist has been added. Properly redirect to Biosec main page
                messages.success(request, "200", extra_tags='add-checklist')
                return redirect('/biosecurity/' + farmID)
        
            else:
                # (ERROR) Incomplete input/s for Biosecurity Checklist
                debug("ERROR: Incomplete input/s for Biosecurity Checklist.")
                messages.error(request, "Incomplete input/s for Biosecurity Checklist.", extra_tags='add-checklist')
                return redirect('/biosecurity/' + farmID)
        else:
            # (ERROR) Invalid farmID
            debug("ERROR: Invalid/None-type farmID from parameter.")
            messages.error(request, "Farm record not found.", extra_tags='add-checklist')
            return redirect('/biosecurity')

    else:
        # (ERROR) not an AJAX Post request
        messages.error(request, "Incomplete input/s for Biosecurity Checklist.", extra_tags='add-checklist')
        return redirect('/biosecurity/' + farmID)

def delete_bioChecklist(request, biosecID):
    """
    (POST-AJAX) For deleting a biosecurity checklist based on biosecID
    """

    if request.is_ajax and request.method == 'POST':

        print("TEST LOG: in delete_bioChecklist()/n")

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
            
            debug("in delete_bioChecklist() -- bioID: " + str(bioID)) 

            # TODO: check if this does DELETE-CASCADE
            extBio = ExternalBiosec.objects.filter(id=bioID).delete()
            intBio = InternalBiosec.objects.filter(id=bioID).delete()

            # TODO: if to be deleted Biochecklist is the FK in Farms, replace Farm int-extbio FK w/ 
            # 2nd latest biosec

            # (SUCCESS) Biosec record has been deleted.
            # return JsonResponse({"instance": jsonStr}, status=200)
            return JsonResponse({"success": "Biosecurity record has been deleted."}, status=200)

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

    # # (1) Get all Farms under the logged-in technician User
    techID = request.user.id

    # collect all IDs of assigned areas under technician
    areaQry = Area.objects.filter(tech_id=techID).all()
    print("TEST LOG areaQry: " + str(areaQry))

    # array to store all farms under each area
    techFarmsList = []

    for area in areaQry :
        # print(str(area.id) + str(area.area_name))

        # collect the corresponding hog raiser details for each farm 
        techFarmQry  = Farm.objects.filter(area_id=area.id).values(
            "id"
        ).all()
        # debug("techFarmQry -- " + str(techFarmQry))

        # pass all data into an array
        for farm in techFarmQry:
            farmObject = {
                "id": str(farm["id"]),
            }
            techFarmsList.append(farmObject)

    # debug("techFarmsList -- " + str(techFarmsList))

    # # Get ID of first farm under technician
    firstFarm = str(*techFarmsList[0].values())
    farmID = int(firstFarm)

    # # if not farmlistQry.exists() or farm.id is None: # for checking Farms that have no Biosec records
    # #     messages.error(request, "Farm record/s not found.", extra_tags="view-biochecklist")
    # #     return redirect('/biosecurity')
    # # else: 
    # farmID = farm.id
    # farmID = 4

    debug("biosec_view() farmID -- " + str(farmID))
    # ------------------

    # Get current internal and external FKs
    currbioQuery = Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').all()
    
    # debug("in biosec_view(): currbioObj")
    # debug(Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').values())

    # (2) Get latest instance of Biochecklist
    currbioObj = currbioQuery.first()
    # print("TEST LOG biosec_view(): Queryset currbio-- " + str(currbioQuery.query))


    # (3) Get all biosecID, last_updated in extbio under a Farm
    extQuery = ExternalBiosec.objects.filter(ref_farm_id=farmID).only(
        'last_updated',
    ).order_by('-last_updated')

    if not extQuery.exists(): # for checking Farms that have no Biosec records
        messages.error(request, "No biosecurity records for this farm.", extra_tags="view-biochecklist")
        return redirect('/biosecurity')


    # print("TEST LOG biosec_view(): Queryset external-- " + str(extQuery.query))
    print("TEST LOG currbioQuery len(): " + str(len(currbioQuery)))


    # (4) GET ACTIVITIES
    actQuery = Activity.objects.filter(ref_farm_id=farmID).filter(is_approved=True).all().order_by('-date')

    actList = []

    # store all data to an array
    for activity in actQuery:
        actList.append({
            'id' : activity.id,
            'date' : activity.date,
            'trip_type' : activity.trip_type,
            'time_departure' : activity.time_departure,
            'time_arrival' : activity.time_arrival,
            'description' : activity.description,
            'remarks' : activity.remarks,
        })

    # pass in context:
    # - (1) farmIDs under Technician user, 
    # - (2) latest intbio-extbio Checklist, 
    # - (3) all biocheck IDs and dates within that Farm, 
    # - (4) activities
    return render(request, 'farmstemp/biosecurity.html', {'farmID' : farmID, 'farmList': techFarmsList,'currBio': currbioObj, 'bioList': extQuery, 'activity' : actList}) 

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
    # print("TEST LOG areaQry: " + str(areaQry))

    # array to store all farms under each area
    techFarmsList = []

    for area in areaQry :
        # print(str(area.id) + str(area.area_name))

        # collect the corresponding hog raiser details for each farm 
        techFarmQry  = Farm.objects.filter(area_id=area.id).values(
            "id"
        ).all()
        # debug("techFarmQry -- " + str(techFarmQry))

        # pass all data into an array
        for farm in techFarmQry:
            farmObject = {
                "id": str(farm["id"]),
            }
            techFarmsList.append(farmObject)

    # debug("techFarmsList -- " + str(techFarmsList))

    # if not farmlistQry.exists() or farmID is None: # for checking Farms that have no Biosec records
    #     messages.error(request, "Farm record/s not found.", extra_tags="view-biochecklist")
    #     return render(request, 'farmstemp/biosecurity.html', {})
    # else: 
    # Get farmID passed from URL param
    farmID = farmID
    debug("in select_biosec() farmID -- " + str(farmID))


    # Select Biochecklist with latest date
    currbioQuery = Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').all()
    
    # debug("in select_biosec(): currbioObj")
    # debug(Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').values())

    # (2) Get latest instance of Biochecklist
    currbioObj = currbioQuery.first()
    # print("TEST LOG biosec_view(): Queryset currbio-- " + str(currbioQuery.query))


    # (3) Get all biosecID, last_updated in extbio under a Farm
    extQuery = ExternalBiosec.objects.filter(ref_farm_id=farmID).only(
        'last_updated',
    ).order_by('-last_updated')

    # print("TEST LOG biosec_view(): Queryset external-- " + str(extQuery.query))
    print("TEST LOG currbioQuery len(): " + str(len(currbioQuery)))


    # (4) GET ACTIVITIES
    actQuery = Activity.objects.filter(ref_farm_id=farmID).filter(is_approved=True).all().order_by('-date')

    actList = []
    # print(str(now(settings.TIME_ZONE)))

    # store all data to an array
    for activity in actQuery:
        # print(str((localtime() - activity.last_updated).days))
        # print(str(localtime() - activity.last_updated))
        
        # check if activity record date is still within the 24 hour mark of current time
        # if activity.last_updated >= localtime() :
        # if (activity.last_updated - localtime()).total_seconds() > 86400 :
        if (localtime() - activity.last_updated).days == 0:
            # print(str(activity.last_updated))
            editable = True
        else : 
            editable = False

        actList.append({
            'id' : activity.id,
            'date' : activity.date,
            'trip_type' : activity.trip_type,
            'time_departure' : activity.time_departure,
            'time_arrival' : activity.time_arrival,
            'description' : activity.description,
            'remarks' : activity.remarks,
            'editable' : editable
        })
    
    # if request.method == 'POST' :
    #     activityForm = ActivityForm(request.POST)
    #     activity.save()
    # else :
    #     activityForm = ActivityForm()

    # print("TEST LOG actList: " + str(actList))

    # pass in context:
    # - (1) farmIDs under Technician user, 
    # - (2) latest intbio-extbio Checklist, 
    # - (3) all biocheck IDs and dates within that Farm, 
    # - (4) activities
    return render(request, 'farmstemp/biosecurity.html', {'farmID' : farmID, 'farmList': techFarmsList,'currBio': currbioObj, 'bioList': extQuery, 'activity' : actList}) 

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
    ).values()
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
    
    return response()

def formsApproval(request):
    return render(request, 'farmstemp/forms-approval.html', {})

def selectedForm(request):
    return render(request, 'farmstemp/selected-form.html', {})


def addActivity(request, farmID):
    """
    - Redirect to Add Activity Page and render corresponding Django form
    - Add new activity to database (will be sent for approval by asst. manager)
    - Save details to activity and add FK of current farm table
    - Django forms will first check the validity of input (based on the fields within models.py)

    farmID - selected farmID passed as parameter
    """

    # collected farmID of selected tech farm
    farmQuery = Farm.objects.get(pk=farmID)
    
    if request.method == 'POST':
        print("TEST LOG: Activity Form has POST method") 
        print(request.POST)

        activityForm = ActivityForm(request.POST)

        # pass all values into each of the array activityList
        activityList = []

        i = 0
        for date in request.POST.getlist('date', default=None):
            activityObject = {
                "date" : request.POST.getlist('date', default=None)[i],
                "trip_type" : request.POST.getlist('trip_type', default=None)[i],
                "time_arrival" : request.POST.getlist('time_arrival', default=None)[i],
                "time_departure" : request.POST.getlist('time_departure', default=None)[i],
                "description" : request.POST.getlist('description', default=None)[i],
                "remarks" : request.POST.getlist('remarks', default=None)[i],
            }
            
            activityList.append(activityObject)

            i += 1
        
        # print("TEST LOG activityList: " + str(activityList))

        if activityForm.is_valid():

            # pass all activityList objects into Activity model
            x = 0

            for act in activityList:
                act = activityList[x]
                # print("TEST LOG Activity " + str(x) + ": " + str(activityList[x]))

                # create new instance of Activity model
                activity = Activity.objects.create(
                    ref_farm = farmQuery,
                    date = act['date'],
                    trip_type = act['trip_type'],
                    time_arrival = act['time_arrival'],
                    time_departure = act['time_departure'],
                    description = act['description'],
                    remarks = act['remarks']
                )

                print(str(activity))

                activity.save()
                print("TEST LOG: Added new activity")

                x += 1
            
            return redirect('/biosecurity/' + str(farmID))
            
        else:
            print("TEST LOG: activityForm is not valid")
            print(activityForm.errors)

    else:
        print("TEST LOG: Activity Form is not a POST method")

        # if form has no input yet, only display an empty form
        activityForm = ActivityForm()

    # pass django form and farmID to template
    return render(request, 'farmstemp/add-activity.html', { 'activityForm' : activityForm, 'farmID' : farmID })

def deleteActivity(request, farmID, activityID):
    """
    - Delete selected activity under current farm
    
    activityID - selected activityID passed as parameter
    farmID - selected farmID passed as parameter
    """
    
    if request.method == 'POST':
        print("TEST LOG: Delete Activity is a POST Method")
    
        Activity.objects.filter(id=activityID).delete()
        return JsonResponse({"success": "Activity has Feen deleted."}, status=200)

    return JsonResponse({"error": "Not a POST method"}, status=400)

def memAnnouncements(request):
    return render(request, 'farmstemp/mem-announce.html', {})

def createAnnouncement(request):
    return render(request, 'farmstemp/create-announcement.html', {})

def viewAnnouncement(request):
    return render(request, 'farmstemp/view-announcement.html', {})

def farmsAssessment(request):
    return render(request, 'farmstemp/rep-farms-assessment.html', {})

def intBiosecurity(request):
    return render(request, 'farmstemp/rep-int-biosec.html', {})

def extBiosecurity(request):
    return render(request, 'farmstemp/rep-ext-biosec.html', {})
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
            "updated": str(f["last_updated"])
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
    - Display all farms assigned to currently logged in technician. 
    - Will only display the approved farms.
    """
    
    # get all farms under the current technician 
    # collect the corresponding hog raiser details for each farm 
    techFarmQry  = Farm.objects.select_related('hog_raiser').annotate(
                fname=F("hog_raiser__fname"), lname=F("hog_raiser__lname"), contact=F("hog_raiser__contact_no")).values(
                        "id",
                        "fname",
                        "lname", 
                        "contact", 
                        "farm_address",
                        "last_updated" )
    # debug(techFarmQry)

    # pass all data into an array
    techFarmsList = []
    for farm in techFarmQry:
        farmObject = {
            "code": str(farm["id"]),
            "raiser": " ".join((farm["fname"],farm["lname"])),
            "contact": farm["contact"],
            "address": farm["farm_address"],
            "updated": str(farm["last_updated"])
        }

        techFarmsList.append(farmObject)
    
    # pass techFarmsList array to template
    return render(request, 'farmstemp/tech-farms.html', {'techFarms' : techFarmsList}) 

def techSelectedFarm(request, farmID):
    """
    - Display details of the selected farm under the currently logged in technician.
    - Will collect the hog raiser, area, internal and external biosecurity, and pigpen measures connected to the farm.   
    """

    # get details of selected farm
    # collect the corresponding details for: hog raiser, area, internal and external biosecurity, and pigpen measures
    techFarmQry = Farm.objects.filter(id=farmID).select_related('hog_raiser', 'area', 'intbio', 'extbio', 'pigpen_measures').annotate(
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
        "fiveh_m_dist"
    ).first()

    # pass selTechFarm object to template   
    return render(request, 'farmstemp/tech-selected-farm.html', selTechFarm)

def addFarm(request):
    """
    - Redirect to Add Farm Page and render corresponding Django form
    - Add new farm to database (will be sent for approval by asst. manager)
    - Save details to hog_raiser, farm, pigpen_measure, externalbiosec and internalbiosec, and area tables
    - Django forms will first check the validity of input (based on the fields within models.py)
    """
    
    if request.method == 'POST':
        print("TEST LOG: Form has POST method") 
        print(request.POST)

        hogRaiserForm       = HogRaiserForm(request.POST)
        farmForm            = FarmForm(request.POST)
        areaForm            = AreaForm(request.POST)
        pigpenMeasuresForm  = PigpenMeasuresForm(request.POST)
        externalBiosecForm  = ExternalBiosecForm(request.POST)
        internalBiosecForm  = InternalBiosecForm(request.POST)
    
        if hogRaiserForm.is_valid():
            hogRaiser = hogRaiserForm.save(commit=False)
            hogRaiser.save()

            print("TEST LOG: Added new raiser")

            if externalBiosecForm.is_valid():
                externalBiosec = externalBiosecForm.save(commit=False)
                externalBiosec.save()

                print("TEST LOG: Added new external biosec")

                if internalBiosecForm.is_valid():
                    internalBiosec = internalBiosecForm.save(commit=False)
                    internalBiosec.save()

                    print("TEST LOG: Added new internal biosec")
                    
                    if areaForm.is_valid():
                        area = areaForm.save(commit=False)
                        area.save()
                        
                        print("TEST LOG: Added area")

                        if farmForm.is_valid():
                            farm = farmForm.save(commit=False)

                            farm.hog_raiser_id = hogRaiser.id
                            farm.extbio_id = externalBiosec.id
                            farm.intbio_id = internalBiosec.id
                            farm.area_id = area.id

                            # get recently created internal and external biosec ID


                            # update ref_farm_id of both records


                            farm.save()
                            
                            print("TEST LOG: Added new farm")

                            if pigpenMeasuresForm.is_valid():
                                pigpenMeasures = pigpenMeasuresForm.save(commit=False)

                                pigpenMeasures.farm_id = farm.id

                                # add all num_heads (pigpen measure) for total_pigs (farm)


                                # update total_pigs of newly added farm


                                pigpenMeasures.save()

                                print("TEST LOG: Added new pigpen measure")
                                return render(request, 'home.html', {})

                            else:
                                print("TEST LOG: Pigpen Measures Form not valid")
                                print(pigpenMeasuresForm.errors)
                        
                        else:
                            print("TEST LOG: Farm Form not valid")
                            print(farmForm.errors)
                    
                    else:
                        print("TEST LOG: Area Form not valid")
                        print(areaForm.errors)

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
        areaForm            = AreaForm()
        pigpenMeasuresForm  = PigpenMeasuresForm()
        externalBiosecForm  = ExternalBiosecForm()
        internalBiosecForm  = InternalBiosecForm()

    # pass django forms to template
    return render(request, 'farmstemp/add-farm.html', {'hogRaiserForm' : hogRaiserForm,
                                                        'farmForm' : farmForm,
                                                        'areaForm' : areaForm,
                                                        'pigpenMeasuresForm' : pigpenMeasuresForm,
                                                        'externalBiosecForm' : externalBiosecForm,
                                                        'internalBiosecForm' : internalBiosecForm})
 

# (POST-AJAX) For searching a Biosec Checklist based on biosecID; called in AJAX request
def search_bioChecklist(request, biosecID):
    if request.is_ajax and request.method == 'POST':
        # Queryset: Get only relevant fields for biochecklist based on biosecID
        """
        SELECT id,<checklist fields from EXTERNAL>,<checklist fields from INTERNAL>
        FROM ExternalBiosec, InternalBiosec 
        WHERE id=biosecID
        """
        print("TEST LOG: in search_bioChecklist()")

        # access biosecID passed from AJAX post request
        # TODO: error handling if biosecID None
        # bioID = request.POST.get("biosecID")
        bioID = biosecID

        if None:
            print("TEST LOG: no biosecID from AJAX req")
        else:
            print("bioID: " + str(bioID))


        # can be filtered by biosecID only, since bioIDs passed in dropdown is w/in Farm
        ext = ExternalBiosec.objects.filter(id=bioID).only(
            'prvdd_foot_dip',      
            'prvdd_alco_soap',     
            'obs_no_visitors',     
            'prsnl_dip_footwear',  
            'prsnl_sanit_hands',   
            'chg_disinfect_daily'
        ).first()
        # print("TEST LOG search_bioCheck(): Queryset-- " + str(querysetExt.query))

        inter = InternalBiosec.objects.filter(id=bioID).only(
            'disinfect_prem',      
            'disinfect_vet_supp',     
        ).first()

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

        jsonStr = json.dumps(bioDict)

        # send to client side (js)
        return JsonResponse({"instance": jsonStr}, status=200)

    # TODO: update accurate error code 

    return JsonResponse({"error": "in search_Checklist() -- not an AJAX POST request"}, status=400)
      
# (POST-AJAX) For updating a Biosec Checklist based on biosecID
def update_bioChecklist(request, biosecID):
    if request.is_ajax and request.method == 'POST':
        # Queryset: Get only relevant fields for biochecklist based on biosecID
        """
        UPDATE <external bio>,<internal bio>
        SET extbio.<biosec field> = value1, intbio.<biosec field>, ...
        WHERE extbioID = <biosecID>;
        """
        print("TEST LOG: in update_bioChecklist()/n")

        # access biosecID from AJAX url param
        bioID = biosecID

        # access checkArr from AJAX post
        chArr = []
        chArr = request.POST.getlist("checkArr[]")

        for index, value in enumerate(chArr): 
            if value is None:
                debug("No value for chArr")
            else:
                # convert str element to int
                int(value)
                print(list((index, value)))

        if bioID is None:
            debug("TEST LOG: no biosecID from AJAX req")
        else:
            print("bioID: " + str(bioID)) 

        extBio = ExternalBiosec.objects.get(pk=bioID)
        # extBio.last_updated = str(now)
        extBio.prvdd_foot_dip       = chArr[0]
        extBio.prvdd_alco_soap      = chArr[1]
        extBio.obs_no_visitors      = chArr[2]
        extBio.prsnl_dip_footwear   = chArr[3]
        extBio.prsnl_sanit_hands    = chArr[4]
        extBio.chg_disinfect_daily  = chArr[5]

        intBio = InternalBiosec.objects.get(pk=bioID)
        # intBio.last_updated = str(now)
        intBio.disinfect_prem       = chArr[6]
        intBio.disinfect_vet_supp   = chArr[7]

        # save in Biosec models
        extBio.save()
        intBio.save()

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

        jsonStr = json.dumps(bioDict)
        
        # send to client side (js)
        return JsonResponse({"instance": jsonStr}, status=200)

    # TODO: update accurate error code

    

    return JsonResponse({"error": "not an AJAX post request"}, status=400)

# For getting all Biosec checklist versions under a Farm.
def biosec_view(request):
    print("TEST LOG: in Biosec view/n")

    """
    SELECT biosec.id,<biochecklist fields INTERNAL>, <biochecklist fields EXTERNAL>
    FROM farm F
    JOIN externalbiosec EXT
    ON F.extbiosec_ID = EXT.id
    JOIN internalbiosec INT
    ON F.intbiosec_ID = INT.id
    """
    # TODO: get farmID, Int or Ext biosec FK id from template (w/c template?)
    # farmID = request.POST.<farmID_name_here> OR request.session['farm_id'] = farmID 
    # bioID = request.POST.<biosecID_name_here>
    
    # (1) Get all Farms under a technician User
    techID = request.user.id
    areaQry = Area.objects.filter(tech_id=techID).values("id")

    debug("areaQry.id -- " + str(areaQry))

    farmlistQry = Farm.objects.filter(Q(area_id=1)|Q(area_id=2)).only(
        "id"
    ).all()

    debug("farmlistQry -- " + str(farmlistQry))

    # Select Biochecklist from intbio-extbio FKs
    farm = farmlistQry.first()
    farmID = farm.id

    debug("biosec_view() farmID -- " + str(farmID))

    # getting current internal and external FKs
    currbioQuery = Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').all()
    
    # (2) Get latest instance of Biochecklist
    currbioObj = currbioQuery.first()
    # print("TEST LOG biosec_view(): Queryset currbio-- " + str(currbioQuery.query))

    # bioID = currbioObj.id
    # debug("bioID -- " + str(bioID))

    # (3) Get all biosecID, last_updated in extbio under a Farm
    """
    SELECT "farmsapp_externalbiosec"."id", "farmsapp_externalbiosec"."last_updated" 
    FROM "farmsapp_externalbiosec" WHERE "farmsapp_externalbiosec"."ref_farm_id" = <farm id> 
    ORDER BY "farmsapp_externalbiosec"."last_updated" DESC
    """
    extQuery = ExternalBiosec.objects.filter(ref_farm_id=farmID).only(
        'last_updated',
    ).order_by('-last_updated')

    print("TEST LOG biosec_view(): Queryset external-- " + str(extQuery.query))

    print("TEST LOG currbioQuery len(): " + str(len(currbioQuery)))

    # debug("currbioObj.intbio.disinfect_vet_supp -- " + str(currbioObj.intbio.disinfect_vet_supp))
    # debug("currbioObj.extbio.prsnl_dip_footwear -- " + str(currbioObj.extbio.prsnl_dip_footwear))

    # set 'farm_id' in the session --> needs to be accessed in addChecklist_view()
    request.session['farm_id'] = farmID 

    # print("TEST LOG: bioInt last_updated-- ")
    # print(bioInt[0].last_updated)

    # (4) GET ACTIVITIES
    actQueury = Activity.objects.filter(ref_farm_id=farmID).all().order_by('-date')

    actList = []

    # store all data to an array
    for activity in actQueury:
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
    return render(request, 'farmstemp/biosecurity.html', {'farmID' : farmID, 'farmList': farmlistQry,'currBio': currbioObj, 'bioList': extQuery, 'activity' : actList}) 

# For getting all Biosec checklist versions under a Farm.
def select_biosec(request, farmID):
    print("TEST LOG: in Biosec view/n")

    """
    SELECT biosec.id,<biochecklist fields INTERNAL>, <biochecklist fields EXTERNAL>
    FROM farm F
    JOIN externalbiosec EXT
    ON F.extbiosec_ID = EXT.id
    JOIN internalbiosec INT
    ON F.intbiosec_ID = INT.id
    """
    # TODO: get farmID, Int or Ext biosec FK id from template (w/c template?)
    # farmID = request.POST.<farmID_name_here> OR request.session['farm_id'] = farmID 
    # bioID = request.POST.<biosecID_name_here>
    
    # (1) Get all Farms under a technician User
    techID = request.user.id
    areaQry = Area.objects.filter(tech_id=techID).first()

    debug("areaQry.id -- " + str(areaQry.id))

    farmlistQry = Farm.objects.filter(area_id=areaQry.id).only(
        "id"
    ).all()

    debug("farmlistQry -- " + str(farmlistQry))

    # Select Biochecklist from intbio-extbio FKs
    # farm = farmlistQry.first()
    # farmID = farm.id

    farmID = farmID
    debug("select_biosec() farmID -- " + str(farmID))

    bioID = 1 
    # select Biochecklist with latest date
    currbioQuery = Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').all()
    
    # (2) Get latest instance of Biochecklist
    currbioObj = currbioQuery.first()
    # print("TEST LOG biosec_view(): Queryset currbio-- " + str(currbioQuery.query))

    # bioID = currbioObj.id
    # debug("bioID -- " + str(bioID))

    # (3) Get all biosecID, last_updated in extbio under a Farm
    """
    SELECT "farmsapp_externalbiosec"."id", "farmsapp_externalbiosec"."last_updated" 
    FROM "farmsapp_externalbiosec" WHERE "farmsapp_externalbiosec"."ref_farm_id" = <farm id> 
    ORDER BY "farmsapp_externalbiosec"."last_updated" DESC
    """
    extQuery = ExternalBiosec.objects.filter(ref_farm_id=farmID).only(
        'last_updated',
    ).order_by('-last_updated')

    print("TEST LOG biosec_view(): Queryset external-- " + str(extQuery.query))

    print("TEST LOG currbioQuery len(): " + str(len(currbioQuery)))

    # debug("currbioObj.intbio.disinfect_vet_supp -- " + str(currbioObj.intbio.disinfect_vet_supp))
    # debug("currbioObj.extbio.prsnl_dip_footwear -- " + str(currbioObj.extbio.prsnl_dip_footwear))

    # set 'farm_id' in the session --> needs to be accessed in addChecklist_view()
    # request.session['farm_id'] = farmID 

    # print("TEST LOG: bioInt last_updated-- ")
    # print(bioInt[0].last_updated)

    # Collecting all activities under selected tech farm
    """
    SELECT farmsapp_activity.id
    FROM farmsapp_activity
    WHERE farmsapp_activity.ref_farm_id = farmID
    ORDER BY farmsapp_activity.date DESC
    """

    actQueury = Activity.objects.filter(ref_farm_id=farmID).all().order_by('-date')

    actList = []

    # store all data to an array
    for activity in actQueury:
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
    return render(request, 'farmstemp/biosecurity.html', {'farmID' : farmID, 'farmList': farmlistQry,'currBio': currbioObj, 'bioList': extQuery, 'activity' : actList}) 

def addChecklist_view(request, farmID):
    # TODO: How to access farmID hidden input tag? through js?
    # TODO: from Biosec page, pass farmID here

    print("TEST LOG: in addChecklist_view/n")

    # get 'farm_id' from the session
    # farm_id = request.session['farm_id']
    farm_id = farmID
    print("TEST LOG: farm_id -- " + str(farm_id))

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

# (POST) function for adding a Biosec Checklist
def post_addChecklist(request, farmID):
    print("TEST LOG: in post_addChecklist/n")

    if request.method == "POST":
        
        # TODO: get farmID from hidden input tag
        # TODO: error hadn,iung cjheck if None
        # farmID = request.POST.get("farmID", None)

        farmID = farmID

        print("in POST biochecklist: farmID -- " + str(farmID))
        
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

        print("biosecArr len(): " + str(len(biosecArr)))

        debug("TEST LOG: List of Biocheck values")
        for index, value in enumerate(biosecArr): 
            if value is None:
                debug("ERROR: Index value is None.")
                checkComplete = False
                # (ERROR) Incomplete input/s for Biosecurity Checklist
                messages.error(request, "Incomplete input/s for Biosecurity Checklist.", extra_tags='add-checklist')
                return redirect('biosecurity')

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

            # update biosec FKs in Farm model
            farm = Farm.objects.filter(id=farmID).select_related("intbio").first()
            farm.intbio = intBio
            farm.extbio = extBio

            farm.save()

            # Properly redirect to Biosec main page
            return redirect('biosecurity')
        else:
            # (ERROR) Incomplete input/s for Biosecurity Checklist
            debug("ERROR: Incomplete input/s for Biosecurity Checklist.")
            messages.error(request, "Incomplete input/s for Biosecurity Checklist.", extra_tags='add-checklist')
            # return redirect('biosecurity')
            return redirect('/biosecurity/' + farmID)
        
    else:
        # (ERROR) not an AJAX Post request
        messages.error(request, "Incomplete input/s for Biosecurity Checklist.", extra_tags='add-checklist')
        return redirect('biosecurity')


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

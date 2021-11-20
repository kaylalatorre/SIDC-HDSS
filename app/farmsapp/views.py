from django.db.models.expressions import F
from django.forms.formsets import formset_factory

# for page redirection, server response
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound

# for AJAX functions
from django.http import JsonResponse
from django.core import serializers
import json

# for Forms
from .forms import HogRaiserForm, FarmForm, PigpenMeasuresForm, InternalBiosecForm, ExternalBiosecForm, ActivityForm, DeliveryForm

# for storing error messages
from django.contrib import messages

# for Models
from django.views.decorators.csrf import csrf_exempt

# for Model imports
import psycopg2
from .models import ExternalBiosec, InternalBiosec, Farm, Hog_Raiser, Pigpen_Measures, Activity, Delivery

#Creating a cursor object using the cursor() method
from django.shortcuts import render

from datetime import date

# for getting date today
from django.utils.timezone import now 

def debug(m):
    print("------------------------[DEBUG]------------------------")
    print(m)
    print("-------------------------------------------------------")

# Farms Management Module Views

## Farms table for all users except Technicians
def farms(request):
    # :Psuedo::
    # farmsdata = []
    # FOR entry IN QUERY SELECT farms JOIN raiser ORDER BY farm_id
    #   MAP(entry TO farmsdata)
    # OUTPUT farmsdata

    # # create raiser
    # hr = Hog_Raiser(
    #     id                  = 2,
    #     fname               = "Juana",
    #     lname               = "Pedra",
    #     contact_no          = "9089990999"
    # )
    # hr.save()
    # debug("hr_save")
    # # create farm
    # fa = Farm(
    #     id                  = 2,
    #     date_registered     = date(2021,11,8),
    #     farm_address        = "farm_address_2",
    #     area                = "east",
    #     loc_long            = 1,
    #     loc_lat             = 2,
    #     bldg_cap            = 3,
    #     num_pens            = 4,
    #     directly_manage     = False,
    #     total_pigs          = 5,
    #     isolation_pen       = False,
    #     roof_height         = 6,
    #     feed_trough         = False,
    #     bldg_curtain        = False,
    #     medic_tank          = 7,
    #     waste_mgt_septic    = False,
    #     waste_mgt_biogas    = False,
    #     waste_mgt_others    = False,
    #     warehouse_length    = 8,
    #     warehouse_width     = 9,
    #     road_access         = False,
    #     extbio_ID           = None,
    #     intbio_ID           = None,
    #     raiser           = Hog_Raiser.objects.get(id=2),
    #     weight_record_ID    = None,
    #     symptoms_record_ID  = None,
    # )
    # fa.save()
    # debug("fa_save")

    qry = Farm.objects.select_related('hog_raiser').annotate(
            fname=F("hog_raiser__fname"), lname=F("hog_raiser__lname"), contact=F("hog_raiser__contact_no")
            ).values(
                "id",
                "fname",
                "lname", 
                "contact", 
                "farm_address",
                "area",
                "total_pigs",
                "num_pens",
                "date_registered"
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
            "area": str(f["area"]),
            "pigs": str(f["total_pigs"]),
            "pens": str(f["num_pens"]),
            "updated": str(f["date_registered"])
        }
        farmsData.append(farmObject)

    return render(request, 'farmstemp/farms.html', {"farms":farmsData}) ## Farms table for all users except Technicians

def selectedFarm(request):
    return render(request, 'farmstemp/selected-farm.html', {})

## Redirect to Add Farm Page and render form
def addFarm(request):
    print("TEST LOG: Add Farm view") 
    
    if request.method == 'POST':
        print("TEST LOG: Form has POST method") 
        print(request.POST)

        hogRaiserForm       = HogRaiserForm(request.POST)
        farmForm            = FarmForm(request.POST)
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

                    if farmForm.is_valid():
                        farm = farmForm.save(commit=False)

                        farm.hog_raiser_id = hogRaiser.id
                        farm.extbio_id = externalBiosec.id
                        farm.intbio_id = internalBiosec.id
                        
                        farm.save()
                        
                        print("TEST LOG: Added new farm")

                        if pigpenMeasuresForm.is_valid():
                            pigpenMeasures = pigpenMeasuresForm.save(commit=False)

                            pigpenMeasures.farm_id = farm.id

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
                    print("TEST LOG: Internal Biosec Form not valid")
                    print(internalBiosec.errors)

            else:
                print("TEST LOG: External Biosec Form not valid")
                print(externalBiosec.errors)
            
        else:
            print("TEST LOG: Hog Raiser Form not valid")
            print(hogRaiserForm.errors)
     
    else:
        print("TEST LOG: Form is not a POST method")
        
        hogRaiserForm       = HogRaiserForm()
        farmForm            = FarmForm()
        pigpenMeasuresForm  = PigpenMeasuresForm()
        externalBiosecForm  = ExternalBiosecForm()
        internalBiosecForm  = InternalBiosecForm()

    return render(request, 'farmstemp/add-farm.html', {'hogRaiserForm' : hogRaiserForm,
                                                        'farmForm' : farmForm,
                                                        'pigpenMeasuresForm' : pigpenMeasuresForm,
                                                        'externalBiosecForm' : externalBiosecForm,
                                                        'internalBiosecForm' : internalBiosecForm})
 

# (GET-AJAX) For searching a Biosec Checklist based on biosecID; called in AJAX request
@csrf_exempt
def search_bioChecklist(request):
    if request.is_ajax and request.method == 'POST':
        # Queryset: Get only relevant fields for biochecklist based on biosecID
        """
        SELECT id,<checklist fields from EXTERNAL>,<checklist fields from INTERNAL>
        FROM ExternalBiosec, InternalBiosec 
        WHERE id=biosecID
        """
        print("TEST LOG: in search_bioChecklist()")

        # access biosecID passed from AJAX post request
        bioID = request.POST.get("biosecID")

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
@csrf_exempt
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
    
    farmID = 1
    bioID = 1 
    # select Biochecklist with latest date
    currbioQuery = Farm.objects.filter(id=farmID).select_related('intbio').select_related('extbio').all()
    
    # gets latest instance of Biochecklist
    currbioObj = currbioQuery.first()

    print("TEST LOG biosec_view(): Queryset currbio-- " + str(currbioQuery.query))


    # select only biosecID, last_updated under a Farm
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
    # pass (1) farmID, (2) latest Checklist, (3) all biocheck id and dates within that Farm
    return render(request, 'farmstemp/biosecurity.html', {'currBio': currbioObj, 'bioList': extQuery}) 


def addChecklist_view(request):
    # TODO: How to access farmID hidden input tag? through js?
    # TODO: from Biosec page, pass farmID here

    print("TEST LOG: in addChecklist_view/n")

    # get 'farm_id' from the session
    farm_id = request.session['farm_id']
    print("TEST LOG: farm_id -- " + str(farm_id))

    return render(request, 'farmstemp/add-checklist.html', {'farmID': farm_id})

def techSelectedFarm(request):
    return render(request, 'farmstemp/tech-selected-farm.html', {})

def techAssignment(request):
    return render(request, 'farmstemp/assignment.html', {})

def formsApproval(request):
    return render(request, 'farmstemp/forms-approval.html', {})

def selectedForm(request):
    return render(request, 'farmstemp/selected-form.html', {})

# (POST) function for adding a Biosec Checklist
def post_addChecklist(request):
    print("TEST LOG: in post_addChecklist/n")

    if request.method == "POST":
        
        # TODO: get farmID from hidden input tag
        farmID = request.POST.get("farmID", None)

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
                messages.error(request, "Incomplete input/s for Biosecurity Checklist.")
                return redirect('biosecurity')

            int(value)
            print(list((index, value)))

        if checkComplete: # (SUCCESS) Checklist input complete, proceed to add in db
            # init Biosec Models
            extBio = ExternalBiosec() #TODO: convert to a filter query --> extQuery = ExternalBiosec.objects.filter(ref_farm_id=farmID)
            intBio = InternalBiosec() #TODO: convert to a filter query
            farmQuery = Farm.objects.get(pk=farmID)

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
            messages.error(request, "Incomplete input/s for Biosecurity Checklist.")
            return redirect('biosecurity')
    else:
        # (ERROR) not an AJAX Post request
        messages.error(request, "Incomplete input/s for Biosecurity Checklist.")
        return redirect('biosecurity')
        

def addActivity(request):
    # print farm ID

    if request.method == 'POST':
        print("TEST LOG: Form has POST method") 
        print(request.POST)

        activityForm = ActivityForm(request.POST)
        deliveryForm = DeliveryForm(request.POST)

            
        if deliveryForm.is_valid():
            delivery = deliveryForm.save(commit=False)
            delivery.save()

            if activityForm.is_valid():
                activty = activityForm.save(commit=False)
                activity.save()
            
            else:
                print("TEST LOG: activityForm is not valid")
                print(activityForm.errors)

        else:
            print("TEST LOG: deliveryForm is not valid")
            print(deliveryForm.errors)
    
    else:
        print("TEST LOG: Form is not a POST method")

        activityForm = ActivityForm()
        deliveryForm = DeliveryForm()
    
    return render(request, 'farmstemp/add-activity.html', {'activityForm' : activityForm,
                                                            'deliveryForm' : deliveryForm})

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

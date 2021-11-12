from django.db.models.expressions import F
from django.forms.formsets import formset_factory

# for page redirection, server response
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound

# for AJAX functions
from django.http import JsonResponse
from django.core import serializers

# for Forms
from .forms import HogRaiserForm, FarmForm, PigpenMeasuresForm, InternalBiosecForm, ExternalBiosecForm, ActivityForm, DeliveryForm

# for Models
from django.views.decorators.csrf import csrf_exempt

# for Model imports
import psycopg2
from .models import ExternalBiosec, InternalBiosec, Farm, Hog_Raiser, Pigpen_Measures, Activity, Delivery

#Creating a cursor object using the cursor() method
from django.shortcuts import render

from datetime import date

def debug(m):
    print("------------------------[DEBUG]------------------------")
    print(m)
    print("-------------------------------------------------------")

# Farms Management Module Views

def farms(request):
    farmsData = []
    for f in Farm.objects.all().values_list():
        farmObject = {
            "code":  str(f[0]),
            "raiser": f[3] + " " + f[4],
            "contact": f[5],
            "address": f[6],
            "area": str(f[8]),
            "pigs": str(f[14]),
            "pens": str(f[12]),
            "updated": str(f[2])
        }
        farmsData.append(farmObject)

    return render(request, 'farmstemp/farms.html', {"farms":farmsData}) ## Farms table for all users except Technicians

def addFarm(request):
    return render(request, 'farmstemp/add-farm.html', {})

@csrf_exempt
# (POST) For searching a Biosec Checklist based on biosecID; called in AJAX request
def search_bioChecklist(request):

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
    querysetExt = ExternalBiosec.objects.filter(id=bioID).only(
        'prvdd_foot_dip',      
        'prvdd_alco_soap',     
        'obs_no_visitors',     
        'prsnl_dip_footwear',  
        'prsnl_sanit_hands',   
        'chg_disinfect_daily'
    )

    print("TEST LOG search_bioCheck(): Queryset-- " + str(querysetExt.query))
    

    querysetInt = InternalBiosec.objects.filter(id=bioID).only(
        'disinfect_prem',      
        'disinfect_vet_supp',     
    ).first()

    # get first instance in query
    bioObj = querysetExt.first()

    # append Internal biosec fields
    bioObj.disinfect_prem       = querysetInt.disinfect_prem
    bioObj.disinfect_vet_supp   = querysetInt.disinfect_vet_supp

    print("TEST LOG search_bioCheck(): querysetInt.disinfect_prem-- " + str(querysetInt.disinfect_prem))
    print("TEST LOG search_bioCheck(): querysetInt.disinfect_vet_supp-- " + str(querysetInt.disinfect_vet_supp))


    # serialize query object into JSON
    ser_instance = serializers.serialize('json', [ bioObj, ])
    # send to client side.
    return JsonResponse({"instance": ser_instance}, status=200)
      
# # (POST) For updating a Biosec Checklist based on biosecID
# def update_bioChecklist(request, id):
    # return render(request, 'farmstemp/biosecurity.html', {})

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

    # print("TEST LOG biosec_view(): Queryset currObj-prvdd_foot_dip--: " + str(currbioObj.extbio.prvdd_foot_dip))

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

    biocheckList = []
    for ext in extQuery:
        biocheckList.append({
            'id':                   ext.id,
            'last_updated':         ext.last_updated, 
        })

    print("TEST LOG biocheckList len(): " + str(len(biocheckList)))
    print("TEST LOG currbioQuery len(): " + str(len(currbioQuery)))

    # set 'farm_id' in the session --> needs to be accessed in addChecklist_view()
    request.session['farm_id'] = farmID 

    # pass (1) farmID, (2) latest Checklist, (3) all biocheck id and dates within that Farm
    return render(request, 'farmstemp/biosecurity.html', {'currBio': currbioObj, 'bioList': biocheckList}) 


def addChecklist_view(request):
    # TODO: How to access farmID hidden input tag? through js?
    # TODO: from Biosec page, pass farmID here

    print("TEST LOG: in addChecklist_view/n")

    # get 'farm_id' from the session
    farm_id = request.session['farm_id']
    print("TEST LOG: farm_id -- " + str(farm_id))

    return render(request, 'farmstemp/add-checklist.html', {'farmID': farm_id})

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

        for index, value in enumerate(biosecArr): 
            if value is None:
                print("No value for radio <input/>")
                checkComplete = False
                # TODO: alert user if incomplete input from the Checklist
                return HttpResponseNotFound('<h1>ERROR: incomplete input from the Checklist</h1>') # for rendering ERROR messages
            else:
                # convert str element to int
                int(value)
                print(list((index, value)))

        if checkComplete:
            # init Biosec Models
            extBio = ExternalBiosec()
            intBio = InternalBiosec()
            farm   = Farm()

            # Put biochecklist attributes into External model
            # TODO: search for Farm object
            farmQuery = Farm.objects.get(pk=farmID)

            # TODO: put farmID to ref_farm_id field
            extBio.ref_farm = farmQuery
            extBio.prvdd_foot_dip       = biosecArr[1]
            extBio.prvdd_alco_soap      = biosecArr[2]
            extBio.obs_no_visitors      = biosecArr[3]
            extBio.prsnl_dip_footwear   = biosecArr[5]
            extBio.prsnl_sanit_hands    = biosecArr[6]
            extBio.chg_disinfect_daily  = biosecArr[7]
            
            # Put biochecklist attributes into Internal model
            # TODO: put farmID to ref_farm_id field
            intBio.ref_farm = farmQuery
            intBio.disinfect_prem      = biosecArr[0]
            intBio.disinfect_vet_supp  = biosecArr[4]

            # Insert data into the INTERNAL, EXTERNAL Biosec tables
            extBio.save()
            intBio.save()

            # TODO: update biosec FKs in Farm model
            # select biosec FKs in Farm
            farm = Farm.objects.filter(id=farmID).select_related("intbio").first()
            farm.intbio = intBio
            farm.extbio = extBio

            farm.save()

            # Properly redirect to Biosec main page
            return redirect('/biosecurity')
        
    else:
        return render(request, 'farmstemp/biosecurity.html', {})
        

def addActivity(request):
    return render(request, 'farmstemp/add-activity.html', {})
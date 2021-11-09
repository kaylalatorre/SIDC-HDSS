from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse
from django.core import serializers

from django.views.decorators.csrf import csrf_exempt


# for Models
from .models import ExternalBiosec, InternalBiosec, Farm
import psycopg2


# class Biochecklist(){

# }


# Farms Management Module Views

def farms(request):
    return render(request, 'farmstemp/farms.html', {}) ## Farms table for all users except Technicians

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


    # TODO: how to select fields from different tables? 
    # --> might need Farm in order to join biosec tables
    querysetExt = ExternalBiosec.objects.filter(id=bioID).only(
        'prvdd_foot_dip',      
        'prvdd_alco_soap',     
        'obs_no_visitors',     
        'prsnl_dip_footwear',  
        'prsnl_sanit_hands',   
        'chg_disinfect_daily'
    )

    print("TEST LOG search_bioCheck(): Queryset-- " + str(querysetExt.query))
    
    # get first instance in query
    bioObj = querysetExt.first()

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
    ORDER BY DESC EXT.last_updated
    """
    # TODO: get farmID from template (w/c template?)
    # farmID = request.POST.<farmID_name_here>

    bioID = 1
    # select Biochecklist with latest date
    # TODO: get Int or Ext biosec FK id from Farm (WHERE in template?)
    currbioQuery = Farm.objects.filter(intbio_id=bioID).select_related('intbio').filter(extbio_id=bioID).select_related('extbio').all()
    # TODO: sort by latest date
    # NOT WORKING: currbioQuery.order_by('-farm.extbio.last_updated').first()
    currbioObj = currbioQuery.first()

    print("TEST LOG biosec_view(): Queryset currObj-prvdd_foot_dip--: " + str(currbioObj.extbio.prvdd_foot_dip))

    print("TEST LOG biosec_view(): Queryset currbio-- " + str(currbioQuery.query))

    farmID = 1
    # select only biosecID, last_updated under a Farm
    # TODO: get farm ID (WHERE in template?)
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

    # pass (1) latest Checklist, (2) all biocheck id and dates within that Farm
    return render(request, 'farmstemp/biosecurity.html', {'currBio': currbioObj, 'bioList': biocheckList}) 



def addChecklist(request):
    return render(request, 'farmstemp/add-checklist.html', {})

# (POST) function for adding a Biosec Checklist
def post_addChecklist(request):
    if request.method == "POST":
        
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

            # Put biochecklist attributes into External model
            extBio.prvdd_foot_dip       = biosecArr[1]
            extBio.prvdd_alco_soap      = biosecArr[2]
            extBio.obs_no_visitors      = biosecArr[3]
            extBio.prsnl_dip_footwear   = biosecArr[5]
            extBio.prsnl_sanit_hands    = biosecArr[6]
            extBio.chg_disinfect_daily  = biosecArr[7]
            
            # Put biochecklist attributes into Internal model
            intBio.disinfect_prem      = biosecArr[0]
            intBio.disinfect_vet_supp  = biosecArr[4]

            # Insert data into the INTERNAL, EXTERNAL Biosec tables
            extBio.save()
            intBio.save()

            # Properly redirect to Biosec main page
            return redirect('/biosecurity')
        
    else:
        return render(request, 'farmstemp/biosecurity.html', {})
        

def addActivity(request):
    return render(request, 'farmstemp/add-activity.html', {})
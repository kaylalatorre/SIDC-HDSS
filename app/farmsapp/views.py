from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.http import JsonResponse
from django.core import serializers

from django.views.decorators.csrf import csrf_exempt


# for Models
from .models import ExternalBiosec, InternalBiosec
import psycopg2


# class Biochecklist(){

# }


# Farms Management Module Views

def farms(request):
    return render(request, 'farmstemp/farms.html', {}) ## Farms table for all users except Technicians

def addFarm(request):
    return render(request, 'farmstemp/add-farm.html', {})

@csrf_exempt
# (POST) For searching a Biosec Checklist based on biosecID
def search_bioChecklist(request):

    # Queryset: Get only relevant fields for biochecklist based on biosecID
    """
    SELECT id,<biochecklist fields>
    FROM ExternalBiosec 
    WHERE id=biosecID
    """
    print("TEST LOG: in search_bioChecklist()")

    # access biosecID passed from AJAX post request
    bioID = request.POST.get("biosecID")

    if None:
        print("TEST LOG: no biosecID from AJAX req")
    else:
        print("bioID: " + str(bioID))


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
    
# # (GET) For updating a Biosec Checklist based on biosecID
# def update_bioChecklist(request, id):
    # return render(request, 'farmstemp/biosecurity.html', {})

# For getting all Biosec checklist versions under a Farm.
def biosec_view(request):
    print("TEST LOG: in Biosec view/n")

    # TODO: How to select biosec checklist under that Farm only? 
    # --> FILTER Int and Ext objects w/ farm ID
    """
    SELECT biosec.id,<biochecklist fields>
    FROM farm F
    JOIN externalbiosec EXT
    ON F.extbiosec_ID = EXT.id
    JOIN internalbiosec INT
    ON F.intbiosec_ID = INT.id
    """

    bioInt = InternalBiosec.objects.all()
    bioExt = ExternalBiosec.objects.all()
    
    # TEST LOG checking
    print("bioInt len(): " + str(len(bioInt)))
    print("bioExt len(): " + str(len(bioExt)))

    print("TEST LOG: bioInt last_updated-- ")
    print(bioInt[0].last_updated)

    # Compile biosec attributes for Checklist, to be passed in template
    # https://stackoverflow.com/questions/58894056/django-create-custom-object-list-in-the-view-and-pass-it-to-template-to-loop-o
    bcheckList = []

    # TODO: How to select relevant fields only from EXTERNAL, INTERNAL models?
    # Populate from External biosec list
    for ext in bioExt:
        bcheckList.append({
            'id': ext.id,
            'last_updated': ext.last_updated, 
            'prvdd_foot_dip': ext.prvdd_foot_dip,     
            'prvdd_alco_soap': ext.prvdd_alco_soap,   
            'obs_no_visitors': ext.obs_no_visitors,    
            'prsnl_dip_footwear': ext.prsnl_dip_footwear,  
            'prsnl_sanit_hands': ext.prsnl_sanit_hands,
            'chg_disinfect_daily': ext.chg_disinfect_daily,
        })

    # Populate from Internal biosec list
    for inter in bioInt:
        bcheckList.append({
            'disinfect_prem': inter.disinfect_prem,
            'disinfect_vet_supp': inter.disinfect_vet_supp,
        })
    
    print("TEST LOG bcheckList len(): " + str(len(bcheckList)))

    return render(request, 'farmstemp/biosecurity.html', {'bioCheck': bcheckList})

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
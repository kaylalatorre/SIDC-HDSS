from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

# for Models
from .models import ExternalBiosec, InternalBiosec
import psycopg2

# Farms Management Module Views

def farms(request):
    return render(request, 'farmstemp/farms.html', {}) ## Farms table for all users except Technicians

def addFarm(request):
    return render(request, 'farmstemp/add-farm.html', {})

def biosecurity(request):
    print("TEST LOG: in Biosec view/n")
    return render(request, 'farmstemp/biosecurity.html', {})

def techSelectedFarm(request):
    return render(request, 'farmstemp/tech-selected-farm.html', {})

def techAssignment(request):
    return render(request, 'farmstemp/assignment.html', {})

def formsApproval(request):
    return render(request, 'farmstemp/forms-approval.html', {})

def selectedForm(request):
    return render(request, 'farmstemp/selected-form.html', {})

def addChecklist(request):
    return render(request, 'farmstemp/add-checklist.html', {})

# POST req function for adding a Biosec Checklist
def post_addChecklist(request):
    if request.method == "POST":
        
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
            # init class Models
            extBio = ExternalBiosec()
            intBio = InternalBiosec()

            # TODO: How will these be updated from Biosec Measures?
            # bird_proof          = models.IntegerField()
            # perim_fence         = models.IntegerField()
            # fiveh_m_dist        = models.IntegerField()
            extBio.prvdd_foot_dip       = biosecArr[1]
            extBio.prvdd_alco_soap      = biosecArr[2]
            extBio.obs_no_visitors      = biosecArr[3]
            extBio.prsnl_dip_footwear   = biosecArr[5]
            extBio.prsnl_sanit_hands    = biosecArr[6]
            extBio.chg_disinfect_daily  = biosecArr[7]
            
            # TODO: How will these be updated from Biosec Measures?
            # isol_pen            = models.IntegerField()
            # waste_mgt           = models.IntegerField()
            # foot_dip            = models.IntegerField()
            intBio.disinfect_prem      = biosecArr[0]
            intBio.disinfect_vet_supp  = biosecArr[4]

            # TODO: insert data into the INTERNAL, EXTERNAL BIOSEC tables
            # extBio.save()
            # intBio.save()

            # Go back to Biosec main page
            return render(request, 'farmstemp/biosecurity.html', {})
        
    else:
        return render(request, 'farmstemp/biosecurity.html', {})
        

def addActivity(request):
    return render(request, 'farmstemp/add-activity.html', {})
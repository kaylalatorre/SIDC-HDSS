from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound

# for Forms
from .forms import HogRaiserForm, FarmForm, PigpenMeasuresForm, InternalBiosecForm, ExternalBiosecForm

# for Models
from .models import ExternalBiosec, InternalBiosec, Farm, Hog_Raiser, Pigpen_Measures

#Creating a cursor object using the cursor() method
from django.shortcuts import render

# Farms Management Module Views

## Farms table for all users except Technicians
def farms(request):
    return render(request, 'farmstemp/farms.html', {}) 

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
    
        # print(pigpenMeasuresForm.errors)

        if farmForm.is_valid() and hogRaiserForm.is_valid() and pigpenMeasuresForm.is_valid() and externalBiosecForm.is_valid() and internalBiosecForm.is_valid():
            hogRaiser      = hogRaiserForm.save(commit=False)
            farm           = farmForm.save(commit=False)
            pigpenMeasures  = pigpenMeasuresForm.save(commit=False)
            externalBiosec = externalBiosecForm.save(commit=False)
            internalBiosec = internalBiosecForm.save(commit=False)

            hogRaiser.save()
            farm.save()
            pigpenMeasures.save()
            externalBiosec.save()
            internalBiosec.save()

            print("TEST LOG: New Farm added to db") 
        
        else:
            # hogRaiserForm       = HogRaiserForm()
            # farmForm            = FarmForm()
            # pigpenMeasuresForm  = PigpenMeasuresForm()
            # externalBiosecForm  = ExternalBiosecForm()
            # internalBiosecForm  = InternalBiosecForm()
            print("TEST LOG: Form not valid")
     
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

## Save Farm Details
def saveFarm(request):
    print("TEST LOG: New Farm added to db") 
    
    return render(request, 'home.html', {}) 
 
def biosec_view(request):
    print("TEST LOG: in Biosec view/n")

    # TODO: For this specific FARM, get all last_updated Dates and biosec checklist fields;
    bioInt = InternalBiosec.objects.all()
    bioExt = ExternalBiosec.objects.all()
    
    # TODO: How to select biosec checklist under that Farm only?

    # FRONTEND: render Date in <select> tag, checklist fields in <table> tag encased in a <form> tag

    print("bioInt len(): " + str(len(bioInt)))
    print("bioExt len(): " + str(len(bioExt)))

    print("TEST LOG: bioInt last_updated-- ")
    # print(bioInt[0].last_updated)

    # TODO: compile biosec attributes for Checklist, pass in template

    return render(request, 'farmstemp/biosecurity.html', {'biosecInt': bioInt, 'biosecExt': bioExt})

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
            # extBio.bird_proof          = 2 # value of 2 is equal to "N/A" in the checklist
            # extBio.perim_fence         = 2
            # extBio.fiveh_m_dist        = 2
            extBio.prvdd_foot_dip       = biosecArr[1]
            extBio.prvdd_alco_soap      = biosecArr[2]
            extBio.obs_no_visitors      = biosecArr[3]
            extBio.prsnl_dip_footwear   = biosecArr[5]
            extBio.prsnl_sanit_hands    = biosecArr[6]
            extBio.chg_disinfect_daily  = biosecArr[7]
            
            # TODO: How will these be updated from Biosec Measures?
            # intBio.isol_pen            = 2
            # intBio.waste_mgt           = 2
            # intBio.foot_dip            = 2
            intBio.disinfect_prem      = biosecArr[0]
            intBio.disinfect_vet_supp  = biosecArr[4]

            # Insert data into the INTERNAL, EXTERNAL BIOSEC tables
            extBio.save()
            intBio.save()

            # Properly redirect to Biosec main page
            return redirect('/biosecurity')
        
    else:
        return render(request, 'farmstemp/biosecurity.html', {})
        

def addActivity(request):
    return render(request, 'farmstemp/add-activity.html', {})

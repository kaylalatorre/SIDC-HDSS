from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound

# for Models
from .models import ExternalBiosec, InternalBiosec
import psycopg2

#Establish connection
conn = psycopg2.connect(
        database = "sidcDB",
        user= "sidcdbuser",
        password = "sidcdb123",
        host = "localhost",
        port = "5432"
)

#Setting auto commit false
conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()
from django.shortcuts import render

# Farms Management Module Views

def farms(request):
    return render(request, 'farmstemp/farms.html', {}) ## Farms table for all users except Technicians

## Add Farm Page
def addFarm(request):
    return render(request, 'farmstemp/add-farm.html', {})

## Save Farm Details
def saveFarm(request):
    # Collect all input
    farmer_code = request.POST.get('input-code')
    raiser_name = request.POST.get('input-name')
    farmer_contact = request.POST.get('input-contact')
    # directly_manage = request.POST.get('cb-directly')

    farmer_address = request.POST.get('input-address')
    # area
    roof_height = request.POST.get('input-roof')
    warehouse_length = request.POST.get('wh-length')
    warehouse_width = request.POST.get('wh-width')
    # feeding trough
    bldg_cap = request.POST.get('input-roof')

    # pig pens
    # biosec

    print("NEW FARM CODE: " + farmer_code)
    # print(directly_manage)

    # Transform address to longitude and latitude values

    # Insert farm record to db
    cursor.execute("""INSERT INTO farmsapp_farm(farmer_code, raiser_uname, farmer_contact)
                      VALUES ('911', 'Jack', '0917824')""")
   
    conn.commit()
    print("-- NEW FARM ADDED TO DB --")

    # Closing the connection
    conn.close()
    return render(request, 'farmstemp/farms.html', {}) 

def addFarm(request):
    return render(request, 'farmstemp/add-farm.html', {})

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
    print(bioInt[0].last_updated)

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

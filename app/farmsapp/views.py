from django.db.models.expressions import F
from django.forms.formsets import formset_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from datetime import date
# for Models
from farmsapp.models import Hog_Raiser, Farm, ExternalBiosec, InternalBiosec

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
    #     raiser_ID           = Hog_Raiser.objects.get(id=2),
    #     weight_record_ID    = None,
    #     symptoms_record_ID  = None,
    # )
    # fa.save()
    # debug("fa_save")

    qry = Farm.objects.select_related('raiser_ID').annotate(
            fname=F("raiser_ID__fname"), lname=F("raiser_ID__lname"), contact=F("raiser_ID__contact_no")
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

    return render(request, 'farmstemp/farms.html'
    , {"farms":farmsData}
    ) ## Farms table for all users except Technicians

def selectedFarm(request):
    return render(request, 'farmstemp/selected-farm.html', {})

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


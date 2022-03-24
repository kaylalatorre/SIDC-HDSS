# for page redirection, server response
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, response

# for storing success and error Django messages
from django.contrib import messages

# for Model imports
from django.contrib.auth.models import User
from farmsapp.models import (
    Farm, Area, Hog_Raiser, Farm_Weight, 
    Mortality, Hog_Symptoms, Mortality_Form, 
    Pigpen_Group, Pigpen_Row, Activity)

# for Model CRUD query functions
from django.db.models.expressions import F, Value
from django.db.models import Q
# from django.forms.formsets import formset_factory
from django.db import connections

# for date and time fields in Models
from datetime import date, datetime, timezone, timedelta
from django.utils.timezone import (
    make_aware, # for date and time fields in Models
    now, # for getting date today
    localtime # for getting date today
) 

# for AJAX functions
from django.http import JsonResponse
from django.core import serializers
import json

# for date and time fields in Models
from datetime import date, datetime, timezone, timedelta
from django.utils.timezone import (
    make_aware, # for date and time fields in Models
    now, # for getting date today
    localtime # for getting date today
) 

def debug(m):
    """
    For debugging purposes

    :param m: The message
    :type m: String
    """
    print("------------------------[DEBUG]------------------------")
    print(m)
    print("-------------------------------------------------------")

# (Module 3) Disease Monitoring view functions

def diseaseDashboard(request):
    """
    Load data for highcharts (active incidents, mortalities, active symptoms recorded, and activities)
    """

    if request.method == 'POST':

        data = []

        # arraylist to store name points for each charts
        incSeries = [] 
        mortSeries = []
        symSeries = []
        actSeries = []

        # get all areas
        areaQry = Area.objects.all()
    
        dateToday = datetime.now(timezone.utc)
        dateMonthsAgo = dateToday - timedelta(30)
        

        # COLLECT ACTIVE/PENDING INCIDENTS PER AREA
        for area in areaQry :
            # print("- - " + str(area.area_name) + " - -")

            # initialize data list per incident; will contain --> [incident date, num. affected pigs]
            incData = []

            # collect all active incidents
            active_incidents = Hog_Symptoms.objects.filter(ref_farm__area__area_name=area.area_name).filter(~Q(report_status="Resolved")).filter(date_filed__range=(now()-timedelta(days=30), now())).order_by('date_filed')
            # debug(active_incidents)

            inc_num_pigs = 0
            try:
                inc_currDate = active_incidents.first().date_filed.date()
            except:
                incData.append([dateMonthsAgo.date(), 0])
                incData.append([dateToday.date(), 0])
                incSeries.append([area.area_name, incData])
                continue

            if inc_currDate != dateMonthsAgo.date():
                # start point of series data
                incData.append([dateMonthsAgo.date(), 0])

            for i in active_incidents:
                try:
                    inc_nextDate = i.date_filed.date()
                except:
                    continue

                if inc_currDate == inc_nextDate :
                    inc_num_pigs += i.num_pigs_affected

                else : 
                    incObj = [ inc_currDate, inc_num_pigs ]
                    incData.append(incObj)

                    inc_num_pigs = i.num_pigs_affected
                    inc_currDate = inc_nextDate


            incData.append([inc_currDate, inc_num_pigs]) 

            # end point of series data
            if inc_currDate != dateToday.date():
                incData.append([dateToday.date(), 0])

            # append area name and all incident data lists
            incSeries.append([area.area_name, incData])


        # COLLECT MORTALITY RECORDS PER AREA
        for area in areaQry :
            # print("- - " + str(area.area_name) + " - -")

            # initialize data list per mortality; will contain --> [mortality date, num. affected pigs]
            mortData = []

            # collect all mortality records
            mortality = Mortality.objects.filter(ref_farm__area__area_name=area.area_name).filter(mortality_date__range=(now()-timedelta(days=30), now())).order_by('mortality_date')
            
            mort_num_pigs = 0
            try:
                mort_currDate = mortality.first().mortality_date
            except:
                mortData.append([dateMonthsAgo.date(), 0])
                mortData.append([dateToday.date(), 0])
                mortSeries.append([area.area_name, mortData])
                continue

            if mort_currDate != dateMonthsAgo.date():
                # start point of series data
                mortData.append([dateMonthsAgo.date(), 0])

            for m in mortality:
                try:
                    mort_nextDate = m.mortality_date
                except:
                    continue
                
                if mort_currDate == mort_nextDate :
                    mort_num_pigs += m.num_today
                
                else :
                    mortObj = [ mort_currDate, mort_num_pigs ]
                    mortData.append(mortObj)

                    mort_num_pigs = m.num_today
                    mort_currDate = mort_nextDate

            mortData.append([mort_currDate, mort_num_pigs])

            # end point of series data
            if mort_currDate != dateToday.date():
                mortData.append([dateToday.date(), 0])

            mortSeries.append([area.area_name, mortData])


        # COLLECT ACTIVE/PENDING SYMPTOMS RECORDED PER AREA
        for area in areaQry :
            # print("- - " + str(area.area_name) + " - -")

            symDate = []
            # SYMPTOMS RECORDED
            symptomsQry = Hog_Symptoms.objects.filter(ref_farm__area__area_name=area.area_name).filter(~Q(report_status="Resolved")).filter(date_filed__range=(now()-timedelta(days=30), now())).values(
                        'high_fever'        , #0
                        'loss_appetite'     , #1
                        'depression'        , #2
                        'lethargic'         , #3
                        'constipation'      , #4
                        'vomit_diarrhea'    , #5
                        'colored_pigs'      , #6
                        'skin_lesions'      , #7
                        'hemorrhages'       , #8
                        'abn_breathing'     , #9
                        'discharge_eyesnose', #10
                        'death_isDays'      , #11
                        'death_isWeek'      , #12
                        'cough'             , #13
                        'sneeze'            , #14
                        'runny_nose'        , #15
                        'waste'             , #16
                        'boar_dec_libido'   , #17
                        'farrow_miscarriage', #18
                        'weight_loss'       , #19
                        'trembling'         , #20
                        'conjunctivitis').order_by("date_filed").all()  #21

            symCountList = [0] * 22
            try:
                for sym in symptomsQry:
                    symCountList[0] += sym["high_fever"]
                    symCountList[1] += sym["loss_appetite"]
                    symCountList[2] += sym["depression"]
                    symCountList[3] += sym["lethargic"]

                    symCountList[4] += sym["constipation"]
                    symCountList[5] += sym["vomit_diarrhea"]
                    symCountList[6] += sym["colored_pigs"]
                    symCountList[7] += sym["skin_lesions"]

                    symCountList[8] += sym["hemorrhages"]
                    symCountList[9] += sym["abn_breathing"]
                    symCountList[10] += sym["discharge_eyesnose"]
                    symCountList[11] += sym["death_isDays"]

                    symCountList[12] += sym["death_isWeek"]
                    symCountList[13] += sym["cough"]
                    symCountList[14] += sym["sneeze"]
                    symCountList[15] += sym["runny_nose"]

                    symCountList[16] += sym["waste"]
                    symCountList[17] += sym["boar_dec_libido"]
                    symCountList[18] += sym["farrow_miscarriage"]
                    symCountList[19] += sym["weight_loss"]

                    symCountList[20] += sym["trembling"]
                    symCountList[21] += sym["conjunctivitis"]
            
            except:
                symCountList = [0] * 22
                
            # print(symCountList)
            symData = [ area.area_name, symCountList ]
            symSeries.append(symData)

        
        # get all activity type
        activityTypeQry = Activity.objects.filter(is_approved=True).filter(date__range=(now()-timedelta(days=30), now())).distinct("trip_type")

        # COLLECT ALL ACTIVITIES
        for actType in activityTypeQry:
            # print("- - " + str(actType.trip_type) + " - -")
            
            # initialize data list per activity; will contain --> [activity date, count]
            actData = []

            # collect all activities under specific type
            activities = Activity.objects.filter(trip_type=actType.trip_type).filter(is_approved=True).filter(date__range=(now()-timedelta(days=30), now())).order_by("date")
            # print(activities)

            act_count = 0
            try: 
                act_currDate = activities.first().date
            except:
                actData.append([dateMonthsAgo.date(), 0])
                actData.append([dateToday.date(), 0])
                actSeries.append([actType.trip_type, actData])
                continue

            if act_currDate != dateMonthsAgo.date():
                # start point of series data
                actData.append([dateMonthsAgo.date(), 0])

            for a in activities:
                # print(a.date)

                try:
                    act_nextDate = a.date
                except:
                    continue

                if act_currDate == act_nextDate:
                    act_count += 1

                else:
                    actData.append([ act_currDate, act_count ])

                    act_count = 1
                    act_currDate = act_nextDate

            actData.append([act_currDate, act_count])

            # end point of series data
            if act_currDate != dateToday.date():
                actData.append([dateToday.date(), 0])

            actSeries.append([actType.trip_type, actData])

        # print(incSeries)
        # print(mortSeries)
        # print(symSeries)
        # print(actSeries)

        # append each chart series into one data array
        data.append(incSeries)
        data.append(mortSeries)
        data.append(symSeries)
        data.append(actSeries)

    return JsonResponse(data, safe=False)

def weightRange(request):
    """
    Load data for highcharts (weight range)
    """


    """
    kimi's suggestion for formatting data hek or something // logic na 'di sure // i'll delete this when i code again

    NOTE: Suggested this in accordance to how data is formatted dun sa highcharts, as long
    as nakukuha niyo data, i can format it and loop it properly sa weight-range.js file.
    
    NOTE: IF EVER iba naisip niyong process/logic, okay lang, but refer to the weight-range.js file for the data
    format for the main series and the drilldown series.  

    NOTE: (Question) Dapat ba within the last month 'yung chart? or all time?

    1. declare empty array (dict?) again for series (like weightSeries = [])
    2. get all areas again


    --- main series ---
    3. gawa ng tatlong array (one for each weight range)
    4. while looping through each area, count all fattener hogs within range
            ---> pwede kunin lahat ng hog_weight na connected sa mga farm fattener slips (it FK-ed)
                    then kunin ang area ? maybe may simpler way hehe
    5. store data in an array pwedeng ---> weightRange[areaName][count]
    6. store these three arrays into a mainSeries[] or something like that


    --- drilldown series ---
    NOTE: I think for this one, inevitable na maraming array/object/something pero baka
    may better way kayong maisip !

    7. loop through each area and count all fattener hogs within range
            ---> start with lowest range first
    8. store data in an array, like farmCount[farmID][count]
    9. store each farmCount array in another array (to collect all farms and their count per area per range)
            ---> areaRange[] or something
    10. store areaRange into a drilldownSeries[] or something 


    11. append both mainSeries and drilldownSeries into weightSeries[]
            ---> OR SKIP weightSeries[] altogether and just :
                    data.append(mainSeries)
                    data.append(drilldownSeries)
    """


    if request.method == 'POST':

        data = []

    return JsonResponse(data, safe=False)


def checkDiseaseList(s):
    """
    Helper function for checking symptoms that match possible hog diseases.
    :param s: symptoms list of the Incident record 
    :type s: list
    """

    diseaseList = [] 

    symp_ASF = [s["high_fever"], s["loss_appetite"], s["depression"], s["lethargic"],
                s["vomit_diarrhea"], s["colored_pigs"], s["skin_lesions"], s["hemorrhages"],
                s["abn_breathing"], s["discharge_eyesnose"], s["death_isDays"], s["cough"],
                s["farrow_miscarriage"], s["trembling"], s["conjunctivitis"]
               ]

    symp_CSF = [s["high_fever"], s["loss_appetite"], s["depression"], s["lethargic"],
                s["constipation"], s["vomit_diarrhea"], s["colored_pigs"],
                s["farrow_miscarriage"], s["trembling"], s["conjunctivitis"]
               ]

    symp_IAVS = [s["high_fever"], s["loss_appetite"], s["lethargic"], s["abn_breathing"],
                 s["cough"], s["sneeze"], s["runny_nose"], s["weight_loss"],
                 s["conjunctivitis"]
                ]

    symp_ADV = [s["high_fever"], s["loss_appetite"], s["vomit_diarrhea"], s["skin_lesions"],
                s["death_isDays"], s["sneeze"], s["waste"], s["weight_loss"],
                s["trembling"]
               ]

    symp_PRRS = [s["high_fever"], s["loss_appetite"], s["lethargic"], s["colored_pigs"],
                 s["abn_breathing"], s["cough"], s["sneeze"], s["waste"],
                 s["boar_dec_libido"], s["farrow_miscarriage"]
                ]

    symp_PED = [s["loss_appetite"], s["vomit_diarrhea"], s["death_isWeek"],
                s["boar_dec_libido"], s["farrow_miscarriage"], s["weight_loss"]
               ]

    if all(symp_ASF):
        diseaseList.append("ASF")

    if all(symp_CSF):
        diseaseList.append("ASF")

    if all(symp_IAVS):
        diseaseList.append("IAV-S")

    if all(symp_ADV):
        diseaseList.append("ADV")

    if all(symp_PRRS):
        diseaseList.append("PRRS")
    
    if all(symp_PED):
        diseaseList.append("PED")

    return diseaseList


def diseaseMonitoring(request):
    """
    Gets all Incident (Hog_Symptoms) records within existing dates and all Areas due to no selected filters in dropdown

    (1) date today
    (2) all Area records
    (3) Incident details
        - ID, Farm Code, Area, No. of Pigs Affected, Symptoms, Status, Date Reported
    """

    # for checking if filters were used in the displayed Report
    isFiltered = False

    # (1) for setting Date input filters to today's date
    dateToday = datetime.now(timezone.utc)

    # (2) all Area records
    areaQry = Area.objects.all()

    # (3.1) Incident details
    incidQry = Hog_Symptoms.objects.filter(~Q(report_status="Resolved")).select_related('ref_farm').annotate(
        farm_code = F("ref_farm__id"),
        farm_area = F("ref_farm__area__area_name"),
        ).values(
            "id",
            "farm_code",
            "farm_area",
            "num_pigs_affected",
            "report_status",
            "date_filed"
            ).order_by("date_filed")

    incidList = []
    total_pigs_affect = 0
    for f in incidQry:

        incidObject = {
            "id":                f["id"],
            "farm_code":         f["farm_code"],
            "farm_area":         f["farm_area"],
            "num_pigs_affected": f["num_pigs_affected"],
            "report_status":     f["report_status"],
            "date_filed":        f["date_filed"],
        }
        incidList.append(incidObject)

        total_pigs_affect += f["num_pigs_affected"]

    # (3.2) Incidents Reported (symptoms list)
    symptomsList = Hog_Symptoms.objects.filter(~Q(report_status="Resolved")).values(
            'high_fever'        ,
            'loss_appetite'     ,
            'depression'        ,
            'lethargic'         ,
            'constipation'      ,
            'vomit_diarrhea'    ,
            'colored_pigs'      ,
            'skin_lesions'      ,
            'hemorrhages'       ,
            'abn_breathing'     ,
            'discharge_eyesnose',
            'death_isDays'      ,
            'death_isWeek'      ,
            'cough'             ,
            'sneeze'            ,
            'runny_nose'        ,
            'waste'             ,
            'boar_dec_libido'   ,
            'farrow_miscarriage',
            'weight_loss'       ,
            'trembling'         ,
            'conjunctivitis').order_by("date_filed").all()

    sDiseaseList = []
    for sRow in symptomsList:
        dList = checkDiseaseList(sRow)
        sDiseaseList.append(dList)
        # debug(sDiseaseList)
    

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidList, symptomsList, sDiseaseList)

    return render(request, 'dsstemp/rep-disease-monitoring.html', {"isFiltered": isFiltered, 'dateStart': dateToday,'dateEnd': dateToday,
                                                                    "areaList": areaQry, "incident_symptomsList": incident_symptomsList,
                                                                    "total_pigs_affect": total_pigs_affect})


def filter_incidentRep(request, startDate, endDate, areaName):
    # debug("TEST LOG: in filter_mortalityRep/n")

    """
    Gets all Incident (Hog_Symptoms) records based on (1) date range and (2) area name.

    (1) all Area records
    (2) Incident details
        - ID, Farm Code, Area, No. of Pigs Affected, Symptoms, Status, Date Reported
    """

    # debug("URL params:")
    # debug("startDate -- " + startDate)
    # debug("endDate -- " + endDate)
    # debug("areaName -- " + areaName)


    # convert str Dates to date type; then to a timezone-aware datetime
    sDate = make_aware(datetime.strptime(startDate, "%Y-%m-%d")) 
    eDate = make_aware(datetime.strptime(endDate, "%Y-%m-%d")) + timedelta(1) # add 1 day to endDate

    # debug("converted sDate -- " + str(type(sDate)))
    # debug("converted eDate -- " + str(type(eDate)))

    # for checking if filters were used in the displayed Report
    isFiltered = True

    # to revert endDate to same user date input
    truEndDate = eDate - timedelta(1)

    # (1) all Area records
    areaQry = Area.objects.all()

    if areaName == "All": # (CASE 1) search only by date range
        # debug("TRACE: in areaName == 'All'")

        # (3.1) Incident details
        incidQry = Hog_Symptoms.objects.filter(~Q(report_status="Resolved")).filter(date_filed__range=(sDate, eDate)).select_related('ref_farm').annotate(
            farm_code = F("ref_farm__id"),
            farm_area = F("ref_farm__area__area_name"),
            ).values(
                "id",
                "farm_code",
                "farm_area",
                "num_pigs_affected",
                "report_status",
                "date_filed"
                ).order_by("date_filed")


        if not incidQry.exists(): # (ERROR) No Disease records found.
            messages.error(request, "No Disease records found.", extra_tags="disease-report")
            return render(request, 'dsstemp/rep-disease-monitoring.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})


        incidList = []
        total_pigs_affect = 0
        for f in incidQry:

            incidObject = {
                "id":                f["id"],
                "farm_code":         f["farm_code"],
                "farm_area":         f["farm_area"],
                "num_pigs_affected": f["num_pigs_affected"],
                "report_status":     f["report_status"],
                "date_filed":        f["date_filed"],
            }
            incidList.append(incidObject)

            total_pigs_affect += f["num_pigs_affected"]

        # (3.2) Incidents Reported (symptoms list)
        symptomsList = Hog_Symptoms.objects.filter(~Q(report_status="Resolved")).filter(date_filed__range=(sDate, eDate)).values(
                'high_fever'        ,
                'loss_appetite'     ,
                'depression'        ,
                'lethargic'         ,
                'constipation'      ,
                'vomit_diarrhea'    ,
                'colored_pigs'      ,
                'skin_lesions'      ,
                'hemorrhages'       ,
                'abn_breathing'     ,
                'discharge_eyesnose',
                'death_isDays'      ,
                'death_isWeek'      ,
                'cough'             ,
                'sneeze'            ,
                'runny_nose'        ,
                'waste'             ,
                'boar_dec_libido'   ,
                'farrow_miscarriage',
                'weight_loss'       ,
                'trembling'         ,
                'conjunctivitis').order_by("date_filed").all()
        

    else: # (CASE 2) search by BOTH date range and areaName
        # debug("TRACE: in else/")

        incidQry = Hog_Symptoms.objects.filter(~Q(report_status="Resolved")).filter(date_filed__range=(sDate, eDate)).filter(ref_farm__area__area_name=areaName).select_related('ref_farm').annotate(
            farm_code = F("ref_farm__id"),
            farm_area = F("ref_farm__area__area_name"),
            ).values(
                "id",
                "farm_code",
                "farm_area",
                "num_pigs_affected",
                "report_status",
                "date_filed"
                ).order_by("date_filed")

        if not incidQry.exists(): # (ERROR) No Disease records found.
            messages.error(request, "No Disease records found.", extra_tags="disease-report")
            return render(request, 'dsstemp/rep-disease-monitoring.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})

        incidList = []
        total_pigs_affect = 0
        for f in incidQry:

            incidObject = {
                "id":                f["id"],
                "farm_code":         f["farm_code"],
                "farm_area":         f["farm_area"],
                "num_pigs_affected": f["num_pigs_affected"],
                "report_status":     f["report_status"],
                "date_filed":        f["date_filed"],
            }
            incidList.append(incidObject)

            total_pigs_affect += f["num_pigs_affected"]

        # (3.2) Incidents Reported (symptoms list)
        symptomsList = Hog_Symptoms.objects.filter(~Q(report_status="Resolved")).filter(date_filed__range=(sDate, eDate)).filter(ref_farm__area__area_name=areaName).values(
                'high_fever'        ,
                'loss_appetite'     ,
                'depression'        ,
                'lethargic'         ,
                'constipation'      ,
                'vomit_diarrhea'    ,
                'colored_pigs'      ,
                'skin_lesions'      ,
                'hemorrhages'       ,
                'abn_breathing'     ,
                'discharge_eyesnose',
                'death_isDays'      ,
                'death_isWeek'      ,
                'cough'             ,
                'sneeze'            ,
                'runny_nose'        ,
                'waste'             ,
                'boar_dec_libido'   ,
                'farrow_miscarriage',
                'weight_loss'       ,
                'trembling'         ,
                'conjunctivitis').order_by("date_filed").all()
        

    sDiseaseList = []
    for sRow in symptomsList:
        dList = checkDiseaseList(sRow)
        sDiseaseList.append(dList)
        # debug(sDiseaseList)

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidList, symptomsList, sDiseaseList)


    return render(request, 'dsstemp/rep-disease-monitoring.html', {"isFiltered": isFiltered, 'dateStart': sDate,'dateEnd': truEndDate,
                                                                    "areaList": areaQry, "areaName": areaName,
                                                                    "incident_symptomsList": incident_symptomsList,
                                                                    "total_pigs_affect": total_pigs_affect})

def dashboard_SusCases():
    """
    Returns suspected disease cases from Hog Symptoms for dashboard
    """
    diseaseSymptoms = {
        'ASF': [
            "high_fever", "loss_appetite", "depression", "lethargic",
            "vomit_diarrhea", "colored_pigs", "skin_lesions", "hemorrhages",
            "abn_breathing", "discharge_eyesnose", "death_isDays", "cough",
            "farrow_miscarriage", "trembling", "conjunctivitis"
        ],
        'CSF': [
            "high_fever", "loss_appetite", "depression", "lethargic",
            "constipation", "vomit_diarrhea", "colored_pigs",
            "farrow_miscarriage", "trembling", "conjunctivitis"
        ],
        'IAVS': [
            "high_fever", "loss_appetite", "lethargic", "abn_breathing", 
            "cough", "sneeze", "runny_nose", "weight_loss",
            "conjunctivitis"
        ],
        'ADV': [
            "high_fever", "loss_appetite", "vomit_diarrhea", "skin_lesions",
            "death_isDays", "sneeze", "waste", "weight_loss",
            "trembling"
        ],
        'PRRS': [
            "high_fever", "loss_appetite", "lethargic", "colored_pigs",
            "abn_breathing", "cough", "sneeze", "waste",
            "boar_dec_libido", "farrow_miscarriage"
        ],
        'PED': [
            "loss_appetite", "vomit_diarrhea", "death_isWeek",
            "boar_dec_libido", "farrow_miscarriage", "weight_loss"
        ]
    }

    diseaseInfo = {
        'ASF':  {'farms': [],'hogs': 0,'symptoms': []},
        'CSF':  {'farms': [],'hogs': 0,'symptoms': []},
        'IAVS': {'farms': [],'hogs': 0,'symptoms': []},
        'ADV':  {'farms': [],'hogs': 0,'symptoms': []},
        'PRRS': {'farms': [],'hogs': 0,'symptoms': []},
        'PED':  {'farms': [],'hogs': 0,'symptoms': []},
    }

    cases = Hog_Symptoms.objects.filter(~Q(report_status="Resolved")).filter(date_filed__range=(now()-timedelta(days=120), now())).values(
        'ref_farm_id'       ,
        'num_pigs_affected' ,
        'high_fever'        ,
        'loss_appetite'     ,
        'depression'        ,
        'lethargic'         ,
        'constipation'      ,
        'vomit_diarrhea'    ,
        'colored_pigs'      ,
        'skin_lesions'      ,
        'hemorrhages'       ,
        'abn_breathing'     ,
        'discharge_eyesnose',
        'death_isDays'      ,
        'death_isWeek'      ,
        'cough'             ,
        'sneeze'            ,
        'runny_nose'        ,
        'waste'             ,
        'boar_dec_libido'   ,
        'farrow_miscarriage',
        'weight_loss'       ,
        'trembling'         ,
        'conjunctivitis'
    )
    
    for case in cases:
        currCase = [key for key, val in case.items() if val and key != 'ref_farm_id' and key != 'num_pigs_affected']

        if len(list(set(diseaseSymptoms['ASF'])-set(currCase))) == 0:
            if case['ref_farm_id'] not in diseaseInfo['ASF']['farms']:
                diseaseInfo['ASF']['farms'].append(case['ref_farm_id'])
            diseaseInfo['ASF']['hogs'] += case['num_pigs_affected']
            diseaseInfo['ASF']['symptoms'].extend(
                list(set(diseaseInfo['ASF']['symptoms'])-set(diseaseSymptoms['ASF']).intersection(currCase)) + 
                list(set(diseaseSymptoms['ASF']).intersection(currCase)-set(diseaseInfo['ASF']['symptoms']))
            )

        if len(list(set(diseaseSymptoms['CSF'])-set(currCase))) == 0:
            if case['ref_farm_id'] not in diseaseInfo['CSF']['farms']:
                diseaseInfo['CSF']['farms'].append(case['ref_farm_id'])
            diseaseInfo['CSF']['hogs'] += case['num_pigs_affected']
            diseaseInfo['CSF']['symptoms'].extend(
                list(set(diseaseInfo['CSF']['symptoms'])-set(diseaseSymptoms['CSF']).intersection(currCase)) + 
                list(set(diseaseSymptoms['CSF']).intersection(currCase)-set(diseaseInfo['CSF']['symptoms']))
            )

        if len(list(set(diseaseSymptoms['IAVS'])-set(currCase))) == 0:
            if case['ref_farm_id'] not in diseaseInfo['IAVS']['farms']:
                diseaseInfo['IAVS']['farms'].append(case['ref_farm_id'])
            diseaseInfo['IAVS']['hogs'] += case['num_pigs_affected']
            diseaseInfo['IAVS']['symptoms'].extend(
                list(set(diseaseInfo['IAVS']['symptoms'])-set(diseaseSymptoms['IAVS']).intersection(currCase)) + 
                list(set(diseaseSymptoms['IAVS']).intersection(currCase)-set(diseaseInfo['IAVS']['symptoms']))
            )
        
        if len(list(set(diseaseSymptoms['ADV'])-set(currCase))) == 0:
            if case['ref_farm_id'] not in diseaseInfo['ADV']['farms']:
                diseaseInfo['ADV']['farms'].append(case['ref_farm_id'])
            diseaseInfo['ADV']['hogs'] += case['num_pigs_affected']
            diseaseInfo['ADV']['symptoms'].extend(
                list(set(diseaseInfo['ADV']['symptoms'])-set(diseaseSymptoms['ADV']).intersection(currCase)) + 
                list(set(diseaseSymptoms['ADV']).intersection(currCase)-set(diseaseInfo['ADV']['symptoms']))
            )
        if len(list(set(diseaseSymptoms['PRRS'])-set(currCase))) == 0:
            if case['ref_farm_id'] not in diseaseInfo['PRRS']['farms']:
                diseaseInfo['PRRS']['farms'].append(case['ref_farm_id'])
            diseaseInfo['PRRS']['hogs'] += case['num_pigs_affected']
            diseaseInfo['PRRS']['symptoms'].extend(
                list(set(diseaseInfo['PRRS']['symptoms'])-set(diseaseSymptoms['PRRS']).intersection(currCase)) + 
                list(set(diseaseSymptoms['PRRS']).intersection(currCase)-set(diseaseInfo['PRRS']['symptoms']))
            )

        if len(list(set(diseaseSymptoms['PED'])-set(currCase))) == 0:
            if case['ref_farm_id'] not in diseaseInfo['PED']['farms']:
                diseaseInfo['PED']['farms'].append(case['ref_farm_id'])
            diseaseInfo['PED']['hogs'] += case['num_pigs_affected']
            diseaseInfo['PED']['symptoms'].extend(
                list(set(diseaseInfo['PED']['symptoms'])-set(diseaseSymptoms['PED']).intersection(currCase)) + 
                list(set(diseaseSymptoms['PED']).intersection(currCase)-set(diseaseInfo['PED']['symptoms']))
            )
    
    return diseaseInfo
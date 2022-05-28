# for page redirection, server response
from select import select
from django import http
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, response

# for storing success and error Django messages
from django.contrib import messages

# for Model imports
from django.contrib.auth.models import User
from matplotlib.pyplot import title
from farmsapp.models import (
    Farm, Area, Hog_Raiser, Farm_Weight, 
    Mortality, Hog_Symptoms, Mortality_Form, 
    Pigpen_Group, Pigpen_Row, Activity,
    Disease_Case, Disease_Record, SEIRD_Input,
    SEIRD_Range, Action_Recommendation, Threshold_Values)

# for Model CRUD query functions
from django.db.models.expressions import F, Value
from django.db.models import (Q, Sum)
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

# for seird implementation
from scipy.integrate import odeint
import numpy as np

# for importing function views from cross-app folder
from farmsapp.views import computeBioscore, debug, intBiosecurity
from healthapp.views import compute_MortRate

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

        
        # get all activity types
        actTypes        = ['Delivery of Veterinary Supplies', 'Delivery of Medicine', 'Monthly Inventory', 'Blood Collection',
                            'Vaccinations', 'Inspection', 'Sold Pigs', 'Other']

        i = 0

        # COLLECT ALL ACTIVITIES
        for actType in actTypes:
            # print("- - " + str(actType) + " - -")

            # initialize data list per activity; will contain --> [activity date, count]
            actData = []

            # collect all activities under specific type
            activities = Activity.objects.filter(trip_type=actType).filter(is_approved=True).filter(date__range=(now()-timedelta(days=30), now())).order_by("date")
            # print(activities)

            act_count = 0
            try: 
                act_currDate = activities.first().date
            except:
                actData.append([dateMonthsAgo.date(), 0])
                actData.append([dateToday.date(), 0])
                actSeries.append([actType, actData])
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

            actSeries.append([actType, actData])

            i += 1

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


def checkDiseaseList(s):
    """
    Helper function for checking symptoms that match possible hog diseases.
    :param s: symptoms list of the Incident record 
    :type s: list
    """

    diseaseList = [] 

    symp_ASF = [s["high_fever"], s["loss_appetite"], s["depression"], s["lethargic"],
                s["vomit_diarrhea"], s["colored_pigs"], s["skin_lesions"], s["hemorrhages"],
                s["abn_breathing"], s["discharge_eyesnose"], s["cough"],
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
                s["sneeze"], s["waste"], s["weight_loss"],
                s["trembling"]
               ]

    symp_PRRS = [s["high_fever"], s["loss_appetite"], s["lethargic"], s["colored_pigs"],
                 s["abn_breathing"], s["cough"], s["sneeze"], s["waste"],
                 s["boar_dec_libido"], s["farrow_miscarriage"]
                ]

    symp_PED = [s["loss_appetite"], s["vomit_diarrhea"],
                s["boar_dec_libido"], s["farrow_miscarriage"], s["weight_loss"]
               ]

    if all(symp_ASF):
        diseaseList.append("ASF")

    if all(symp_CSF):
        diseaseList.append("CSF")

    if all(symp_IAVS):
        diseaseList.append("IAV-S")

    if all(symp_ADV):
        diseaseList.append("ADV")

    if all(symp_PRRS):
        diseaseList.append("PRRS")
    
    if all(symp_PED):
        diseaseList.append("PED")

    return diseaseList


def symptomsMonitoring(request):
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
            'high_fever'        ,   'loss_appetite'     ,   'depression'        ,   'lethargic'         ,
            'constipation'      ,   'vomit_diarrhea'    ,   'colored_pigs'      ,   'skin_lesions'      ,
            'hemorrhages'       ,   'abn_breathing'     ,   'discharge_eyesnose',   'death_isDays'      ,
            'death_isWeek'      ,   'cough'             ,   'sneeze'            ,   'runny_nose'        ,
            'waste'             ,   'boar_dec_libido'   ,   'farrow_miscarriage',   'weight_loss'       ,
            'trembling'         ,   'conjunctivitis'
            ).order_by("date_filed").all()

    sDiseaseList = []
    for sRow in symptomsList:
        dList = checkDiseaseList(sRow)
        sDiseaseList.append(dList)
        # debug(sDiseaseList)
    

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidList, symptomsList, sDiseaseList)

    diseaseInfo = {
        'ASF':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'CSF':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'IAVS': {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'ADV':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'PRRS': {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'PED':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'Others':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
    }

    for case,symptoms,diseaseList in incident_symptomsList:
        none_ctr = 0
        incidID = case['id']
        incidID = "{id:03}".format(id = incidID)

        if "ASF" in diseaseList:
            diseaseInfo['ASF']['num_cases'] += 1
            diseaseInfo['ASF']['incidList'].append(incidID)
            diseaseInfo['ASF']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "CSF" in diseaseList:
            diseaseInfo['CSF']['num_cases'] += 1
            diseaseInfo['CSF']['incidList'].append(incidID)
            diseaseInfo['CSF']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "IAV-S" in diseaseList:
            diseaseInfo['IAVS']['num_cases'] += 1
            diseaseInfo['IAVS']['incidList'].append(incidID)
            diseaseInfo['IAVS']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "ADV" in diseaseList:
            diseaseInfo['ADV']['num_cases'] += 1
            diseaseInfo['ADV']['incidList'].append(incidID)
            diseaseInfo['ADV']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "PRRS" in diseaseList:
            diseaseInfo['PRRS']['num_cases'] += 1
            diseaseInfo['PRRS']['incidList'].append(incidID)
            diseaseInfo['PRRS']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "PED" in diseaseList:
            diseaseInfo['PED']['num_cases'] += 1
            diseaseInfo['PED']['incidList'].append(incidID)
            diseaseInfo['PED']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if none_ctr == 6:
            diseaseInfo['Others']['num_cases'] += 1
            diseaseInfo['Others']['incidList'].append(str(incidID))
            diseaseInfo['Others']['hogs_total'] += case['num_pigs_affected']

    if diseaseInfo['ASF']['incidList']:
        diseaseInfo['ASF']['incidStr'] = ', '.join(diseaseInfo['ASF']['incidList'])

    if diseaseInfo['CSF']['incidList']:
        diseaseInfo['CSF']['incidStr'] = ', '.join(diseaseInfo['CSF']['incidList'])

    if diseaseInfo['IAVS']['incidList']:
        diseaseInfo['IAVS']['incidStr'] = ', '.join(diseaseInfo['IAVS']['incidList'])

    if diseaseInfo['ADV']['incidList']:
        diseaseInfo['ADV']['incidStr'] = ', '.join(diseaseInfo['ADV']['incidList'])

    if diseaseInfo['PRRS']['incidList']:
        diseaseInfo['PRRS']['incidStr'] = ', '.join(diseaseInfo['PRRS']['incidList'])

    if diseaseInfo['PED']['incidList']:
        diseaseInfo['PED']['incidStr'] = ', '.join(diseaseInfo['PED']['incidList'])

    if diseaseInfo['Others']['incidList']:
        diseaseInfo['Others']['incidStr'] = ', '.join(diseaseInfo['Others']['incidList'])

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidList, symptomsList, sDiseaseList)

    # debug(diseaseInfo)

    return render(request, 'dsstemp/rep-symptoms-monitoring.html', {"isFiltered": isFiltered, 'dateStart': dateToday,'dateEnd': dateToday,
                                                                    "areaList": areaQry, "incident_symptomsList": incident_symptomsList,
                                                                    "total_pigs_affect": total_pigs_affect, "susCases": diseaseInfo})


def filter_incidentRep(request, startDate, endDate, areaName):
    # debug("TEST LOG: in filter_incidentRep/n")

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
            return render(request, 'dsstemp/rep-symptoms-monitoring.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})


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
            'high_fever'        ,   'loss_appetite'     ,   'depression'        ,   'lethargic'         ,
            'constipation'      ,   'vomit_diarrhea'    ,   'colored_pigs'      ,   'skin_lesions'      ,
            'hemorrhages'       ,   'abn_breathing'     ,   'discharge_eyesnose',   'death_isDays'      ,
            'death_isWeek'      ,   'cough'             ,   'sneeze'            ,   'runny_nose'        ,
            'waste'             ,   'boar_dec_libido'   ,   'farrow_miscarriage',   'weight_loss'       ,
            'trembling'         ,   'conjunctivitis'
            ).order_by("date_filed").all()
        

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
            return render(request, 'dsstemp/rep-symptoms-monitoring.html', {"areaName": areaName,"isFiltered": isFiltered,'areaList': areaQry,'dateStart': sDate,'dateEnd': truEndDate})

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
            'high_fever'        ,   'loss_appetite'     ,   'depression'        ,   'lethargic'         ,
            'constipation'      ,   'vomit_diarrhea'    ,   'colored_pigs'      ,   'skin_lesions'      ,
            'hemorrhages'       ,   'abn_breathing'     ,   'discharge_eyesnose',   'death_isDays'      ,
            'death_isWeek'      ,   'cough'             ,   'sneeze'            ,   'runny_nose'        ,
            'waste'             ,   'boar_dec_libido'   ,   'farrow_miscarriage',   'weight_loss'       ,
            'trembling'         ,   'conjunctivitis'
            ).order_by("date_filed").all()
        

    sDiseaseList = []
    for sRow in symptomsList:
        dList = checkDiseaseList(sRow)
        sDiseaseList.append(dList)
        # debug(sDiseaseList)

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidList, symptomsList, sDiseaseList)

    diseaseInfo = {
        'ASF':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'CSF':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'IAVS': {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'ADV':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'PRRS': {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'PED':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
        'Others':  {'num_cases': 0, 'incidList': [], 'incidStr': "", 'hogs_total': 0},
    }

    for case,symptoms,diseaseList in incident_symptomsList:
        none_ctr = 0
        incidID = case['id']
        incidID = "{id:03}".format(id = incidID)

        if "ASF" in diseaseList:
            diseaseInfo['ASF']['num_cases'] += 1
            diseaseInfo['ASF']['incidList'].append(incidID)
            diseaseInfo['ASF']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "CSF" in diseaseList:
            diseaseInfo['CSF']['num_cases'] += 1
            diseaseInfo['CSF']['incidList'].append(incidID)
            diseaseInfo['CSF']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "IAV-S" in diseaseList:
            diseaseInfo['IAVS']['num_cases'] += 1
            diseaseInfo['IAVS']['incidList'].append(incidID)
            diseaseInfo['IAVS']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "ADV" in diseaseList:
            diseaseInfo['ADV']['num_cases'] += 1
            diseaseInfo['ADV']['incidList'].append(incidID)
            diseaseInfo['ADV']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "PRRS" in diseaseList:
            diseaseInfo['PRRS']['num_cases'] += 1
            diseaseInfo['PRRS']['incidList'].append(incidID)
            diseaseInfo['PRRS']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if "PED" in diseaseList:
            diseaseInfo['PED']['num_cases'] += 1
            diseaseInfo['PED']['incidList'].append(incidID)
            diseaseInfo['PED']['hogs_total'] += case['num_pigs_affected']
        else: none_ctr += 1

        if none_ctr == 6:
            diseaseInfo['Others']['num_cases'] += 1
            diseaseInfo['Others']['incidList'].append(incidID)
            diseaseInfo['Others']['hogs_total'] += case['num_pigs_affected']


        # combine the 2 previous queries into 1 temporary list
        incident_symptomsList = zip(incidList, symptomsList, sDiseaseList)

        # debug(diseaseInfo)

    if diseaseInfo['ASF']['incidList']:
        diseaseInfo['ASF']['incidStr'] = ', '.join(diseaseInfo['ASF']['incidList'])

    if diseaseInfo['CSF']['incidList']:
        diseaseInfo['CSF']['incidStr'] = ', '.join(diseaseInfo['CSF']['incidList'])

    if diseaseInfo['IAVS']['incidList']:
        diseaseInfo['IAVS']['incidStr'] = ', '.join(diseaseInfo['IAVS']['incidList'])

    if diseaseInfo['ADV']['incidList']:
        diseaseInfo['ADV']['incidStr'] = ', '.join(diseaseInfo['ADV']['incidList'])

    if diseaseInfo['PRRS']['incidList']:
        diseaseInfo['PRRS']['incidStr'] = ', '.join(diseaseInfo['PRRS']['incidList'])

    if diseaseInfo['PED']['incidList']:
        diseaseInfo['PED']['incidStr'] = ', '.join(diseaseInfo['PED']['incidList'])

    if diseaseInfo['Others']['incidList']:
        diseaseInfo['Others']['incidStr'] = ', '.join(diseaseInfo['Others']['incidList'])

    return render(request, 'dsstemp/rep-symptoms-monitoring.html', {"isFiltered": isFiltered, 'dateStart': sDate,'dateEnd': truEndDate,
                                                                    "areaList": areaQry, "areaName": areaName,
                                                                    "incident_symptomsList": incident_symptomsList,
                                                                    "total_pigs_affect": total_pigs_affect, "susCases": diseaseInfo})

def dashboard_SusCases():
    """
    Returns suspected disease cases from Hog Symptoms for dashboard
    """
    diseaseSymptoms = {
        'ASF': [
            "high_fever", "loss_appetite", "depression", "lethargic",
            "vomit_diarrhea", "colored_pigs", "skin_lesions", "hemorrhages",
            "abn_breathing", "discharge_eyesnose", "cough",
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
            "sneeze", "waste", "weight_loss",
            "trembling"
        ],
        'PRRS': [
            "high_fever", "loss_appetite", "lethargic", "colored_pigs",
            "abn_breathing", "cough", "sneeze", "waste",
            "boar_dec_libido", "farrow_miscarriage"
        ],
        'PED': [
            "loss_appetite", "vomit_diarrhea",
            "boar_dec_libido", "farrow_miscarriage", "weight_loss"
        ]
    }

    diseaseInfo = {
        'ASF':  {'diseaseList': [], 'hogs_total': 0},
        'CSF':  {'diseaseList': [], 'hogs_total': 0},
        'IAVS': {'diseaseList': [], 'hogs_total': 0},
        'ADV':  {'diseaseList': [], 'hogs_total': 0},
        'PRRS': {'diseaseList': [], 'hogs_total': 0},
        'PED':  {'diseaseList': [], 'hogs_total': 0},
        'Others':  {'diseaseList': [], 'hogs_total': 0},

    }


    incidCases = Hog_Symptoms.objects.filter(~Q(report_status="Resolved")).filter(date_filed__range=(now()-timedelta(days=120), now())).values(
        'id'                ,       'ref_farm_id'       ,       'num_pigs_affected' ,       'high_fever'        ,       'loss_appetite'     ,
        'depression'        ,       'lethargic'         ,       'constipation'      ,       'vomit_diarrhea'    ,       'colored_pigs'      ,       
        'skin_lesions'      ,       'hemorrhages'       ,       'abn_breathing'     ,       'discharge_eyesnose',       'death_isDays'      ,
        'death_isWeek'      ,       'cough'             ,       'sneeze'            ,       'runny_nose'        ,       'waste'             ,       
        'boar_dec_libido'   ,       'farrow_miscarriage',       'weight_loss'       ,       'trembling'         ,       'conjunctivitis'
    )
    
    # debug(incidCases)

    # get Disease Cases with status "1" (Negative) or "2" (Pending)
    diseaseCases = Disease_Case.objects.filter(~Q(lab_result=True)).filter(date_updated__range=(now()-timedelta(days=120), now())).annotate(
        high_fever          =F('incid_case__high_fever')        ,       loss_appetite       =F('incid_case__loss_appetite')     ,
        depression          =F('incid_case__depression')        ,       lethargic           =F('incid_case__lethargic')         ,
        constipation        =F('incid_case__constipation')      ,       vomit_diarrhea      =F('incid_case__vomit_diarrhea')    ,
        colored_pigs        =F('incid_case__colored_pigs')      ,       skin_lesions        =F('incid_case__skin_lesions')      ,
        hemorrhages         =F('incid_case__hemorrhages')       ,       abn_breathing       =F('incid_case__abn_breathing')     ,
        discharge_eyesnose  =F('incid_case__discharge_eyesnose'),       death_isDays        =F('incid_case__death_isDays')      ,
        death_isWeek        =F('incid_case__death_isWeek')      ,       cough               =F('incid_case__cough')             ,
        sneeze              =F('incid_case__sneeze')            ,       runny_nose          =F('incid_case__runny_nose')        ,
        waste               =F('incid_case__waste')             ,       boar_dec_libido     =F('incid_case__boar_dec_libido')   ,
        farrow_miscarriage  =F('incid_case__farrow_miscarriage'),       weight_loss         =F('incid_case__weight_loss')       ,
        trembling           =F('incid_case__trembling')         ,       conjunctivitis      =F('incid_case__conjunctivitis')    ,
        num_negative        =F('incid_case__num_pigs_affected') - F('num_pigs_affect')
    ).values(
        'incid_case__id'                ,        'incid_case__ref_farm_id'       ,        'incid_case__num_pigs_affected' ,        'lab_result'                    ,        
        'lab_ref_no'                    ,        'high_fever'                    ,        'loss_appetite'                 ,        'depression'                    ,        
        'lethargic'                     ,        'constipation'                  ,        'vomit_diarrhea'                ,        'colored_pigs'                  ,        
        'skin_lesions'                  ,        'hemorrhages'                   ,        'abn_breathing'                 ,        'discharge_eyesnose'            ,        
        'death_isDays'                  ,        'death_isWeek'                  ,        'cough'                         ,        'sneeze'                        ,        
        'runny_nose'                    ,        'waste'                         ,        'boar_dec_libido'               ,        'farrow_miscarriage'            ,        
        'weight_loss'                   ,        'trembling'                     ,        'conjunctivitis'                ,        'disease_name'                  ,
        'num_negative'
    )

    for case in incidCases:
        none_ctr = 0 # counter for no detected exact disease given the symptoms
        currCase = [key for key, val in case.items() if val and key not in ['id', 'ref_farm_id', 'num_pigs_affected']]

        if len(list(set(diseaseSymptoms['ASF'])-set(currCase))) == 0:
            diseaseInfo['ASF']['diseaseList'].append({'incid_id': case['id'], 'farm_id': case['ref_farm_id'], 'hogs_affect': case['num_pigs_affected'], 'symptoms': currCase})
            diseaseInfo['ASF']['hogs_total'] += case['num_pigs_affected']
        else:
            none_ctr += 1

        if len(list(set(diseaseSymptoms['CSF'])-set(currCase))) == 0:
            diseaseInfo['CSF']['diseaseList'].append({'incid_id': case['id'], 'farm_id': case['ref_farm_id'], 'hogs_affect': case['num_pigs_affected'], 'symptoms': currCase})
            diseaseInfo['CSF']['hogs_total'] += case['num_pigs_affected']
        else:
            none_ctr += 1

        if len(list(set(diseaseSymptoms['IAVS'])-set(currCase))) == 0:
            diseaseInfo['IAVS']['diseaseList'].append({'incid_id': case['id'], 'farm_id': case['ref_farm_id'], 'hogs_affect': case['num_pigs_affected'], 'symptoms': currCase})
            diseaseInfo['IAVS']['hogs_total'] += case['num_pigs_affected']
        else:
            none_ctr += 1

        if len(list(set(diseaseSymptoms['ADV'])-set(currCase))) == 0:
            diseaseInfo['ADV']['diseaseList'].append({'incid_id': case['id'], 'farm_id': case['ref_farm_id'], 'hogs_affect': case['num_pigs_affected'], 'symptoms': currCase})
            diseaseInfo['ADV']['hogs_total'] += case['num_pigs_affected']
        else:
            none_ctr += 1

        if len(list(set(diseaseSymptoms['PRRS'])-set(currCase))) == 0:
            diseaseInfo['PRRS']['diseaseList'].append({'incid_id': case['id'], 'farm_id': case['ref_farm_id'], 'hogs_affect': case['num_pigs_affected'], 'symptoms': currCase})
            diseaseInfo['PRRS']['hogs_total'] += case['num_pigs_affected']
        else:
            none_ctr += 1

        if len(list(set(diseaseSymptoms['PED'])-set(currCase))) == 0:
            diseaseInfo['PED']['diseaseList'].append({'incid_id': case['id'], 'farm_id': case['ref_farm_id'], 'hogs_affect': case['num_pigs_affected'], 'symptoms': currCase})
            diseaseInfo['PED']['hogs_total'] += case['num_pigs_affected']
        else:
            none_ctr += 1
        
        # check for cases with no exact disease diagnosis
        if none_ctr == 6:
            diseaseInfo['Others']['diseaseList'].append({'incid_id': case['id'], 'farm_id': case['ref_farm_id'], 'hogs_affect': case['num_pigs_affected'], 'symptoms': currCase})
            diseaseInfo['Others']['hogs_total'] += case['num_pigs_affected']
    # debug(diseaseInfo)

    for dcase in diseaseCases:
        # debug(dcase)
        dcurrCase = [key for key, val in dcase.items() if val and key not in ['incid_case__id', 'incid_case__ref_farm_id', 'incid_case__num_pigs_affected', 'lab_result', 'lab_ref_no', 'disease_name', 'num_negative']]
        dname = dcase['disease_name']
        
        if dname == 'ASF':
            diseaseInfo['ASF']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no'],
                'negative': dcase['num_negative']
                })
            diseaseInfo['ASF']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'CSF':
            diseaseInfo['CSF']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no'],
                'negative': dcase['num_negative']
                })
            diseaseInfo['CSF']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'IAVS':
            diseaseInfo['IAVS']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no'],
                'negative': dcase['num_negative']
                })
            diseaseInfo['IAVS']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'ADV':
            diseaseInfo['ADV']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no'],
                'negative': dcase['num_negative']
                })
            diseaseInfo['ADV']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'PRRS':
            diseaseInfo['PRRS']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no'],
                'negative': dcase['num_negative']
                })
            diseaseInfo['PRRS']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'PED':
            diseaseInfo['PED']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no'],
                'negative': dcase['num_negative']
                })
            diseaseInfo['PED']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'Others':
            diseaseInfo['Others']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no'],
                'negative': dcase['num_negative']
                })
            diseaseInfo['Others']['hogs_total'] += dcase['incid_case__num_pigs_affected']

    # debug(diseaseInfo)

    return diseaseInfo

def submitLabReport(request, lab_ref):
    """
    AJAX POST. Accept inputs to create a disease case from an incident case
    """

    if request.method == 'POST':
        debug(request.POST)
        lab_ref_no = lab_ref
        disease_name = request.POST.get("disease_name")
        incid_id = request.POST.get("incid_id")
        num_pigs_affect = request.POST.get("lab_result")
        date_updated = datetime.now(timezone.utc)
        lab_result = False
        if int(num_pigs_affect) > 0:
            lab_result = True
        
        try:
            # save disease case
            dCase = Disease_Case(
                disease_name    = disease_name,
                lab_result      = lab_result,
                lab_ref_no      = lab_ref_no,
                date_updated    = date_updated,
                incid_case_id   = incid_id,
                start_date      = date_updated,
                num_pigs_affect = num_pigs_affect 
            )
            dCase.save()
            # get mortalities
            total_died = Mortality.objects.filter(case_no=incid_id, source="incident").aggregate(Sum('num_today'))['num_today__sum']
            # create disease record
            debug("DCASE")
            debug(dCase)
            Disease_Record(
                date_filed          = date_updated,
                num_recovered       = 0,
                num_died            = 0,
                ref_disease_case    = dCase,
                total_died          = 0,
                total_recovered     = 0
            ).save()

            # resolve incident case
            remarks = "Tested positive for " + str(disease_name)
            incid_case = Hog_Symptoms.objects.filter(id=incid_id).first()
            incid_case.report_status="Resolved"
            incid_case.remarks = remarks
            incid_case.save()

            # success response
            return HttpResponse(status=200)
        except:
            # error response
            return HttpResponse(status=500)
            
# data required for disease-monitoring.html in a different url
def diseaseMonitoring(strDisease):
    # Lab Reference	    Incident Involved   	No. of Pigs Affected	Recovered	Died

    data = []
    # debug(request.method)
    # debug(strDisease + " LOAD DISEASE TABLE")

    # confrimed cases
    casesQry = Disease_Record.objects.filter(ref_disease_case__disease_name=strDisease).annotate(
        lab_ref_no       = F("ref_disease_case__lab_ref_no"),
        incid_no         = F("ref_disease_case__incid_case"),
        num_pigs_affect  = F("ref_disease_case__num_pigs_affect"),
        date_updated     = F("ref_disease_case__date_updated"),
    ).order_by("-date_filed", "lab_ref_no").values()
    # debug(casesQry)

    dTable = []
    dTable.append(strDisease)
    # [strDisease, []]

    cases = []
    casesList = []
    for case in casesQry:
        if case['lab_ref_no'] not in casesList:
            casesList.append(case['lab_ref_no'])
            cases.append(case)
            # debug(casesList)
    dTable.append(cases)
    # debug(dTable)

    # Get the parameter values of the disease for the SEIRD model from the database 
    inputQry = SEIRD_Input.objects.filter(disease_name=strDisease).select_related('seird_range').annotate(
        min_incub_days          = F("seird_range__min_incub_days"),
        max_incub_days          = F("seird_range__max_incub_days"),
        
        min_reproduction_num    = F("seird_range__min_reproduction_num"),
        max_reproduction_num    = F("seird_range__max_reproduction_num"),
        
        min_days_can_spread     = F("seird_range__min_days_can_spread"),
        max_days_can_spread     = F("seird_range__max_days_can_spread"),
        
        min_fatality_rate       = F("seird_range__min_fatality_rate"),
        max_fatality_rate       = F("seird_range__max_fatality_rate"),
        
        min_days_til_death      = F("seird_range__min_days_til_death"),
        max_days_til_death      = F("seird_range__max_days_til_death"),

        ).first()
    # debug(inputQry)

    # append data to return (table, SEIRD inputs) 
    data.append(dTable)
    data.append(inputQry)
    # debug(strDisease + "Data")
    # debug(data)

    return data # for disease monitoring dashboard contents

# rendering disease-content.html in a different url
def load_diseaseMonitoring(request, strDisease):
    return render(request, 'dsstemp/dm.html', {"disData": diseaseMonitoring(strDisease)})

# rendering disease-content.html (partial) in a different url
def load_ConfirmedCases(request, strDisease):
    """
    Used for when calling .load 
    """
    return render(request, 'dsstemp/disease-content.html', {"disData": diseaseMonitoring(strDisease)})

def load_diseaseMap(request, strDisease):
    # debug(strDisease + " LOAD DISEASE MAP")
    # debug(request.method)

    # confrimed cases
    casesQry = Disease_Record.objects.filter(ref_disease_case__disease_name=strDisease).annotate(
        loc_long       = F("ref_disease_case__incid_case__ref_farm__loc_long"),
        loc_lat         = F("ref_disease_case__incid_case__ref_farm__loc_lat"),
        num_pigs_affect  = F("ref_disease_case__num_pigs_affect"),
        date_updated     = F("ref_disease_case__date_updated")
    ).order_by("-date_filed", "ref_disease_case_id").values(
        'ref_disease_case_id',
        'total_died',
        'total_recovered',
        'loc_long',
        'loc_lat',
        'num_pigs_affect',
        )

    cases = {}
    casesList = []
    for case in casesQry:
        if case['ref_disease_case_id'] not in casesList:
            casesList.append(case['ref_disease_case_id'])
            try:
                existingCase = cases[str(
                        [case['loc_lat'], case['loc_long']]
                    )]
                existingCase['caseIDs'].append("{:03d}".format(case['ref_disease_case_id']))
                existingCase['total_died'] += case['total_died']
                existingCase['total_recovered'] += case['total_recovered']
                existingCase['num_pigs_affect'] += case['num_pigs_affect']
            except:
                cases[str(
                        [case['loc_lat'], case['loc_long']]
                    )]={
                        'caseIDs':["{:03d}".format(case['ref_disease_case_id'])],
                        'loc_lat': case['loc_lat'],
                        'loc_long': case['loc_long'],
                        'total_died': case['total_died'],
                        'total_recovered': case['total_recovered'],
                        'num_pigs_affect': case['num_pigs_affect']
                    }
    
    # debug(cases)
    # debug(list(cases.values()))

    return JsonResponse(list(cases.values()), safe=False) # for disease monitoring dashboard contents

def load_diseaseChart(request, strDisease):

    data = []
    # debug(request.method)
    # debug(strDisease + " LOAD DISEASE CHART")    

    dChart = {
        'confirmed': [],
        'recovered': [],
        'died': [] }

    # prepare time range of line chart
    dateToday = datetime.now(timezone.utc)
    dateMonthsAgo = dateToday - timedelta(30)

    # get all disease_record with diseas_name
    dcasesQry = Disease_Record.objects.filter(ref_disease_case__disease_name=strDisease).filter(
        date_filed__range=(now()-timedelta(days=30), now())).annotate(
            confirmed_pigs = F("ref_disease_case__num_pigs_affect")
        ).order_by("date_filed").all()
    # debug(dcasesQry)

    confirmedCtr = 0
    recoveredCtr = 0
    diedCtr      = 0
    case_currDate = 0

    # NULL case      
    try:
        case_currDate = dcasesQry.first().date_filed
    except:
        pass

    if case_currDate != dateMonthsAgo.date():
        # start point of series data
        dChart['confirmed'].append([dateMonthsAgo.date(), 0])
        dChart['recovered'].append([dateMonthsAgo.date(), 0])
        dChart['died'].append([dateMonthsAgo.date(), 0])

    dCaseList = []
    for d in dcasesQry:
        # debug(case_currDate)
        # debug(d.date_filed)

        try:
            case_nextDate = d.date_filed
        except:
            continue

        # for confirmed cases not yet in the
        if case_currDate == case_nextDate:
            if d.ref_disease_case_id not in dCaseList:
                dCaseList.append(d.ref_disease_case_id)
                confirmedCtr += d.confirmed_pigs
            
            recoveredCtr += d.num_recovered
            diedCtr += d.num_died

        else :
            if confirmedCtr > 0:
                # append finalized [date, count]
                caseObj = [ case_currDate, confirmedCtr ]
                dChart['confirmed'].append(caseObj)
            if recoveredCtr > 0:
                dChart['recovered'].append([ case_currDate, recoveredCtr ])
            if diedCtr > 0:    
                dChart['died'].append([ case_currDate, diedCtr ])

            # move to next date
            if d.ref_disease_case_id not in dCaseList:
                dCaseList.append(d.ref_disease_case_id)
                confirmedCtr = d.confirmed_pigs
            else:
                confirmedCtr = 0

            recoveredCtr = d.num_recovered
            diedCtr = d.num_died
            case_currDate = case_nextDate

    if confirmedCtr > 0:
        dChart['confirmed'].append([case_currDate, confirmedCtr])
    if recoveredCtr > 0:
        dChart['recovered'].append([ case_currDate, recoveredCtr ])
    if diedCtr > 0:
        dChart['died'].append([ case_currDate, diedCtr ])

    # end point of series data
    # debug(case_currDate)
    # debug(dateToday.date())

    if case_currDate != dateToday.date():
        dChart['confirmed'].append([dateToday.date(), 0])
        dChart['recovered'].append([dateToday.date(), 0])
        dChart['died'].append([dateToday.date(), 0])
    else:
        dChart['confirmed'].append([case_currDate, confirmedCtr])
        dChart['recovered'].append([ case_currDate, recoveredCtr ])
        dChart['died'].append([ case_currDate, diedCtr ])
        
    # debug(dChart)

    # append data to return (table, line chart, map, SEIRD) 
    data.append(dChart)
    # debug(data)
    return JsonResponse(data, safe=False)
    
class farmDetails:
    def __init__(self, id, morts, mortRt, acts, aCases, pCases, oCases, latestBio, intScore, extScore):
        actList = ['Inspection', 'Vaccinations', 'Delivery of Medicine', 'Delivery of Veterinary Supplies']
        self.id = id
        self.mortalities = morts
        self.mortalityRate = mortRt
        self.activities = acts
        self.missingActs = list(set(actList)-set(list(acts)))
        self.activeCases = aCases
        self.pendingCases = pCases
        self.ogDCases = oCases
        self.lastUpdateBiosec = latestBio
        self.intbio_score = intScore
        self.extbio_score = extScore
    def __str__(self):
        return str({
            'id':self.id,
            'mortalities':self.mortalities,
            'mortalityRate':self.mortalityRate,
            'missingActs':self.missingActs,
            'activeCases':self.activeCases,
            'pendingCases':self.pendingCases,
            'ogDCases':self.ogDCases,
            'lastUpdateBiosec':self.lastUpdateBiosec,
            'intbio_score':self.intbio_score,
            'extbio_score':self.extbio_score
        })
def getAxRMort(score, mortThresh, areaFarms):
    aXr = {
        'analysis_mortality':[],
        'analysis_activities':[],
        'analysis_cases':[],
        'recommendations':[]}
    
    for farm in areaFarms:
        if len(farm.missingActs) != 0:
            aXr['analysis_activities'].append("- Farm {id:03} has not done the following activities in the past week: [{activities}]".format(id=farm.id, activities=', '.join(farm.missingActs)))
        if farm.activeCases != 0 or farm.pendingCases != 0 or farm.ogDCases != 0:
            aXr['analysis_cases'].append("- Farm {id:03} has {aCase} active cases, {pCase} pending cases, and {oCase} on going cases".format(id=farm.id, aCase=farm.activeCases, pCase=farm.pendingCases, oCase=farm.ogDCases))
    if score == 0:
        needInspect = []
        for farm in areaFarms:
            if farm.mortalities != 0:
                aXr['analysis_mortality'].append("- Farm {id:03} has {morts} mortalities to date".format(id=farm.id, morts=farm.mortalities))
            if (now().date() - farm.lastUpdateBiosec).days > 14:
                needInspect.append("{:03}".format(farm.id))
        aXr['recommendations'].append("- Farms [{}] have not been inspected for the past 2 weeks. Inspect accordingly.".format(", ".join(needInspect)))
    
    elif score == 1:
        mortRts = {}
        for farm in areaFarms:
            mortRts["{:03}".format(farm.id)] = farm.mortalityRate
        if mortRts:
            highestMort = list(dict(sorted(mortRts.items(), key=lambda x:x[1], reverse=True)[0: 1]).keys())[0]

            aXr['analysis_mortality'].append("- Farm {} currently has the highest mortality rate in the area".format(highestMort))
            aXr['recommendations'].append("- Farm {} has the highest mortality rate in the area. Inspect this Farm and nearby farms in the area.".format(highestMort))
    
    elif score == 2:
        mortFarms = []
        missingActivities = []
        for farm in areaFarms:
            missingActivities += farm.missingActs
            if farm.mortalityRate > mortThresh - 2:
                mortFarms.append("{:03}".format(farm.id))
        aXr['analysis_mortality'].append("- These farms currently are around 2% away from the threshold: [{}]".format(", ".join(mortFarms)))
        baseRec = "- Do the following for each farms in the area:\n"
        inspectRec="inspect within the week\n"
        resourceRec=""
        missingActivities = sorted(set(missingActivities))
        if len(missingActivities) != 0:
            resourceRec="allot resources for:\n [{}]".format(", ".join(missingActivities))

        aXr['recommendations'].append(baseRec + inspectRec + resourceRec)

    elif score == 3:
        mortFarms = []
        missingActivities = []
        for farm in areaFarms:
            missingActivities += farm.missingActs
            if farm.mortalityRate > mortThresh - 1:
                mortFarms.append("{:03}".format(farm.id))
        aXr['analysis_mortality'].append("- These farms currently are around 1% away from the threshold: [{}]".format(", ".join(mortFarms)))
        baseRec = "- Do the following for each farms in the area:\n"
        inspectRec="inspect within the week\n"
        resourceRec=""
        missingActivities = sorted(set(missingActivities))
        if len(missingActivities) != 0:
            resourceRec="allot resources for:\n [{}]".format(", ".join(missingActivities))
    
        aXr['recommendations'].append(baseRec + inspectRec + resourceRec)
    elif score == 4:
        mortFarms = []
        missingActivities = []
        for farm in areaFarms:
            missingActivities += farm.missingActs
            if farm.mortalityRate > mortThresh:
                mortFarms.append("{:03}".format(farm.id))
        aXr['analysis_mortality'].append("- These farms currently are over the threshold: [{}]".format(", ".join(mortFarms)))
        baseRec = "- Do the following for each farms in the area:\n"
        inspectRec="inspect within the week\n"
        resourceRec=""
        reportRec="prepare reports on farms and relay to upper management"

        
        missingActivities = sorted(set(missingActivities))
        if len(missingActivities) != 0:
            resourceRec="allot resources for: [{}]\n".format(", ".join(missingActivities))

        aXr['recommendations'].append(baseRec + inspectRec + resourceRec + reportRec)
        aXr['recommendations'].append(baseRec + inspectRec + resourceRec)

    return aXr

def getAxRBio(score, areaFarms):
    aXr = {
        'analysis_biosec':[],
        'analysis_activities':[],
        'analysis_inspection':[],
        'recommendations':[]
    }   
    if score == 1:
        needInspection = []
        for farm in areaFarms:
            aXr['analysis_biosec'].append("- The last biosecurity update of farm {id:03} was {days} ago".format(id=farm.id, days=now().date() - farm.lastUpdateBiosec))
            if farm.missingActs is not None:
                aXr['analysis_activities'].append("- Farm {id:03} has not done these activities in the past week:\n{acts}".format(id=farm.id, acts='\n'.join(farm.missingActs)))
            if (now().date() - farm.lastUpdateBiosec).days > 7:
                needInspection.append("{:03}".format(farm.id))
            aXr['analysis_biosec'].sort()
            aXr['analysis_activities'].sort()
            aXr['analysis_inspection'].sort()
        aXr['recommendations'].append("- Biosecurity score is at an optimal state. Maintain or increase biosecurity score through inspecting farms not updated for the past week. ")
        if len(needInspection) != 0:
            aXr['recommendations'].append("- The following farms have not been inspected for the past week: [{}]. Inform Field Technician to schedule inspections.".format(", ".join(needInspection)))
    elif score == 2 or score == 3:
        farmIntBiosec = {}
        farmExtBiosec = {}
        needInspection = []
        for farm in areaFarms:
            farmIntBiosec["{:03}".format(farm.id)] = farm.intbio_score
            farmExtBiosec["{:03}".format(farm.id)] = farm.extbio_score
            farmExtBiosec
            aXr['analysis_biosec'].append("- Farm {id:03} has a internal biosecurity score of {intbio}% and external biosecurity score of {extbio}%".format(id=farm.id, intbio=farm.intbio_score, extbio=farm.extbio_score))
            if now().date() - timedelta(days=7) > farm.lastUpdateBiosec:
                aXr['analysis_biosec'].append("- The last biosecurity update of farm {id:03} was on {date}".format(id=farm.id, date=farm.lastUpdateBiosec))
            if farm.missingActs is not None:
                aXr['analysis_activities'].append("- Farm {id:03} has not done these activities in the past week:\n{acts}".format(id=farm.id, acts='\n'.join(farm.missingActs)))
            if (now().date() - farm.lastUpdateBiosec).days > 7:
                needInspection.append("{:03}".format(farm.id))
        
        aXr['analysis_biosec'].sort()
        aXr['analysis_activities'].sort()
        if len(needInspection) != 0:
            needInspection.sort()
            aXr['analysis_inspection'].append("These farms have not been inspected in the past week:\n[{}]".format(", ".join(needInspection)))
            N = int(len(needInspection)/5) or 1
            lowestInt = dict(sorted(farmIntBiosec.items(), key=lambda x:x[1])[0: N]).keys()
            lowestExt = dict(sorted(farmExtBiosec.items(), key=lambda x:x[1])[0: N]).keys()
            aXr['analysis_inspection'].append("- These farms currently have the lowest internal biosecurity score:\n[{}]".format(", ".join(lowestInt)))
            aXr['analysis_inspection'].append("- These farms currently have the lowest external biosecurity score:\n[{}]".format(", ".join(lowestExt)))

            # recommendations
            aXr['recommendations'].append("- Inspect the following farms: [{}]. Send an announcement to raisers involved.".format(", ".join(needInspection)))
            aXr['recommendations'].append("- View the biosecurity measures and latest biosecurity checklist of farms: [{}].".format(", ".join( sorted(list(set(lowestExt)-set(lowestInt))+list(set(lowestInt)-set(lowestExt))) )))

    return aXr

def getAnalysisAndRecommend(intBioLvl, extBioLvl, mortRtLvl, mortThresh, areaFarms, areaName):
    bioscore = intBioLvl
    if extBioLvl > intBioLvl:
        bioscore = extBioLvl

    mortItem = '{}_Mortality'.format(areaName)
    bioItem='{}_Biosecurity'.format(areaName)
    aXr = {
        mortItem:getAxRMort(mortRtLvl, mortThresh, areaFarms),
        bioItem:getAxRBio(bioscore, areaFarms) 
    }
    aXr[mortItem]['item'] = mortItem
    aXr[bioItem]['item'] = bioItem
    return aXr

def getRecommendations(farmQry, threshVals):
    areaDetails = {}
    
    # abort if threshVals is empty
    try:
        threshVals['Mortality']
        threshVals['Biosecurity']
    except:
        return "Thresholds has not been set"

    actList = ['Inspection', 'Vaccinations', 'Delivery of Medicine', 'Delivery of Veterinary Supplies']
    for f in farmQry:
        # pre req data
        latestPP = Pigpen_Group.objects.filter(ref_farm_id=f["id"]).order_by("-date_added").first()
        biosec_scores = computeBioscore(f["id"], f["intbioID"], f["extbioID"])

        # get values
        mortRate = compute_MortRate(f["id"], None)
        numMortality = Mortality.objects.filter(ref_farm_id=f['id']).filter(mortality_form__pigpen_grp_id=latestPP.id).values_list("num_toDate", flat=True).last()
        # last_updated__range=(now() - timedelta(days=7), now()),
        activities = Activity.objects.filter(ref_farm_id=f['id'], trip_type__in=actList).distinct("trip_type").values_list("trip_type", flat=True)
        incidCases = Hog_Symptoms.objects.filter(ref_farm_id=f["id"]).filter(pigpen_grp_id=latestPP.id)
        ongoingDCases = Disease_Case.objects.filter(incid_case__ref_farm=f["id"]).filter(end_date__isnull=False).count()
        
        currfarm = farmDetails(
            id = f['id'], 
            morts = int(numMortality or 0), 
            mortRt = mortRate, 
            acts = activities,
            aCases = incidCases.filter(report_status="Active").count(),
            pCases = incidCases.filter(report_status="Pending").count(),
            oCases = ongoingDCases,
            latestBio = f['extbio__last_updated'].date(),
            intScore = biosec_scores[0],
            extScore = biosec_scores[1]
        )
        # compile
        try:
            farmArea = areaDetails[f['area__area_name']]
            farmArea['farms'].append(currfarm)
            farmArea['farmIDs'].append('{:03}'.format(f['id']))
            farmArea['mortalityRate'] = round(farmArea['mortalityRate'] + mortRate, 2)
            farmArea['intbio_score'] = round(farmArea['intbio_score'] + biosec_scores[0], 2)
            farmArea['extbio_score'] = round(farmArea['extbio_score'] + biosec_scores[1], 2)            
        except:
            areaDetails[f['area__area_name']] = {
                'farms':[currfarm],
                'farmIDs':['{:03}'.format(f['id'])],
                'mortalityRate': mortRate,
                'intbio_score': biosec_scores[0],
                'extbio_score': biosec_scores[1]
                }

    # make threshold values easier to reference
    

    recommendations = {}
    for area_name in areaDetails:
        """
        Checks:
        > MortThresh        lvl 0       under mort thresh
        > MortThresh - 4    lvl 1       under mort thresh with 4% diff
        > MortThresh - 2    lvl 2       under mort thresh with 2% diff
        > MortThresh - 1    lvl 3       under mort thresh with 1% diff
        > MortThresh        lvl 4       over or equal mort thresh

        >= BioThresh        lvl 0       over or equal biosec thresh
        < BioThresh         lvl 1       over or equal biosec thresh
        < BioThresh - 5     lvl 2       under biosec thresh with a 5% diff
        < BioThresh - 10    lvl 3       under biosec thresh with a 10% diff
        """

        # underIntBio = False
        intbioLvl = 0
        # underExtBio = False
        extbioLvl = 0
        # overMortRt = False
        mortRtLvl = 0

        areaData = areaDetails[area_name]
        ave_intbio_score = round(areaData['intbio_score'] / len(areaData['farmIDs']), 2)
        ave_extbio_score = round(areaData['extbio_score'] / len(areaData['farmIDs']), 2)
        ave_mort_rate = round(areaData['mortalityRate'] / len(areaData['farmIDs']), 2)
        
        if  threshVals['Biosecurity'] > ave_intbio_score:
            intbioLvl = 1
            if  threshVals['Biosecurity'] - 5 > ave_intbio_score:
                intbioLvl = 2
                if  threshVals['Biosecurity'] - 10 > ave_intbio_score:
                    intbioLvl = 3

        if  threshVals['Biosecurity'] > ave_extbio_score:
            extbioLvl = 1
            if  threshVals['Biosecurity'] - 5 > ave_extbio_score:
                extbioLvl = 2
                if  threshVals['Biosecurity'] - 10 > ave_extbio_score:
                    extbioLvl = 3
        
        if  ave_mort_rate > threshVals['Mortality'] - 4 :
            mortRtLvl = 1
            if  ave_mort_rate > threshVals['Mortality'] - 2 :
                mortRtLvl = 2
                if  ave_mort_rate > threshVals['Mortality'] - 1 :
                    mortRtLvl = 3
                    if  ave_mort_rate > threshVals['Mortality']:
                        mortRtLvl = 4
        recommendations.update(getAnalysisAndRecommend(intBioLvl=intbioLvl, extBioLvl=extbioLvl, mortRtLvl=mortRtLvl, mortThresh=threshVals['Mortality'],  areaFarms=areaData['farms'], areaName=area_name))
    return recommendations

def actionRecommendation(request):
    """
    function for Action Recommendation page containing:
    (1) Farm statistics overview
        1.1) ave. internal biosec score
        1.2) ave. external biosec score
        1.3) ave. mortality rate
        1.4) total incident cases (active)
        1.5) total confirmed disease cases
    (2) Set threshold values
    (3) Data for analysis and recommendations table
    """
    
    # Get Farm details 
    farmQry = Farm.objects.select_related('intbio', 'extbio').annotate(
        intbioID = F("intbio__id"),
        extbioID = F("extbio__id"),
        ).values(
            "id",
            "area__area_name",
            "intbioID",
            "extbioID",
            "extbio__last_updated"
            ).order_by("id").all()

    if not farmQry.exists(): 
        messages.error(request, "No farm details found.", extra_tags="action-rec")
        # return render(request, 'dsstemp/action-rec.html', {})

    threshQry = Threshold_Values.objects.values('title', 'value')
    threshVals = {}
    for thresh in threshQry:
        threshVals[thresh['title']] = thresh['value']
    recommendations = getRecommendations(farmQry, threshVals)

    # debug(recommendations)
    ave_intbio = 0
    ave_extbio = 0
    ave_mortRate = 0
    total_active = 0
    total_dcases = 0
    for f in farmQry:
        # (1.1, 1.2) for int and ext biosec scores per Farm (total)
        biosec_score = computeBioscore(f["id"], f["intbioID"], f["extbioID"])

        ave_intbio += biosec_score[0]
        ave_extbio += biosec_score[1]

        # (1.3) for mortality rate per Farm (total)
        ave_mortRate += compute_MortRate(f["id"], None)

        # get latest version of Pigpen
        latestPP = Pigpen_Group.objects.filter(ref_farm_id=f["id"]).order_by("-date_added").first()
        # (1.4) for Hog_Symptoms records with "Active" status (total)
        total_active += Hog_Symptoms.objects.filter(ref_farm_id=f["id"]).filter(pigpen_grp_id=latestPP.id).filter(report_status="Active").count()

        # (1.5) for Confirmed Disease Cases (total) 
        total_dcases += Disease_Case.objects.filter(incid_case__ref_farm=f["id"]).count()


    actionStats = {
        "ave_intbio": round((ave_intbio / len(farmQry)), 2),
        "ave_extbio": round((ave_extbio / len(farmQry)), 2),
        "ave_mort_rate": round((ave_mortRate / len(farmQry)), 2),
        "total_active": total_active,
        "total_dcases": total_dcases,
    }

    return render(request, 'dsstemp/action-rec.html', {"aStats": actionStats, "aRecs": recommendations, 'threshVals': threshVals})


def derivSEIRD(y, t, N, beta, gamma, delta, alpha, rho):
    """
        implementation of model based on: 
        https://github.com/henrifroese/infectious_disease_modelling/blob/master/part_two.ipynb
    """

    S, E, I, R, D = y
    dSdt = -beta * S * I / N
    dEdt = beta * S * I / N - delta * E
    dIdt = delta * E - (1 - alpha) * gamma * I - alpha * rho * I
    dRdt = (1 - alpha) * gamma * I
    dDdt = alpha * rho * I
    
    return dSdt, dEdt, dIdt, dRdt, dDdt


def load_diseaseSeird(request, strDisease):
    """
    # ----INPUT PARAMETERS ----------------------
    # Disease Incubation Period (days) -- [0] delta
    # Basic Reproduction No.           -- [1] beta = R_0 * gamma
    # No. of Days Disease can Spread   -- [2] D 
    # Fatality Rate                    -- [3] alpha
    # No. of Days until Death          -- [4] 1 / rho
    # ---------------------------------------------
    """
    # debug(strDisease + " LOAD SEIRD")
    # compute for total SIDC pig population
    farmQry = Farm.objects.aggregate(Sum("total_pigs"))
    N = farmQry["total_pigs__sum"]

    # get initial parameters from frontend inputs
    sValues = []
    sValues = request.POST.getlist("values[]")
    # debug("VALUES")
    # debug(sValues)
    try:
        sParam = [int(sValues[0]), float(sValues[1]), int(sValues[2]), float(sValues[3]), int(sValues[4])]
        # debug(sParam)
    except:
        params = SEIRD_Input.objects.filter(disease_name=strDisease).first()
        # debug(params)
        sParam = [
            params.incub_days,
            params.reproduction_num,
            params.days_can_spread,
            params.fatality_rate,
            params.days_til_death
        ]

    # debug(sParam)
    # NOTE: CODE BASIS
    # D = 4.0 # infections lasts four days
    # gamma = 1.0 / D
    # delta = 1.0 / 5.0  # incubation period of five days
    # R_0 = 5.0
    # beta = R_0 * gamma  # R_0 = beta / gamma, so beta = R_0 * gamma
    # alpha = 0.2  # 20% death rate
    # rho = 1/9  # 9 days from infection until death
    # S0, E0, I0, R0, D0 = N-1, 1, 0, 0, 0  # initial conditions: one exposed
    
    
    # set params in SEIRD var inputs
    D = sParam[2] # infections lasts four days
    gamma = 1.0 / D
    delta = 1.0 / sParam[0]  # incubation period of five days
    R_0 = sParam[1]
    beta = R_0 * gamma  # R_0 = beta / gamma, so beta = R_0 * gamma
    alpha = sParam[3]  # 20% death rate
    rho = 1/sParam[4]  # 9 days from infection until death
    S0, E0, I0, R0, D0 = N-1, 1, 0, 0, 0  # initial conditions: one exposed

    # t = time (in days)
    t = np.linspace(0, 99, 100) 
    y0 = S0, E0, I0, R0, D0 # initialize SEIRD compartments

    # Feed custom SEIRD function into odeint
    retVal = odeint(derivSEIRD, y0, t, args=(N, beta, gamma, delta, alpha, rho))
    S, E, I, R, D = np.round(retVal.T, 2)
    # debug(retVal)

    # compute for N to check correctness of SEIRD
    x = 0
    totalPigs = []
    for s in S.tolist():
        e = E[x]
        i = I[x]
        r = R[x]
        d = D[x]

        totalPigs.append(round((s + e + i + r + d), 0))
        x += 1

    modelData = [totalPigs, S.tolist(), E.tolist(), I.tolist(), R.tolist(), D.tolist()]
    return JsonResponse(modelData, safe=False)

def saveMortThreshold(request, threshVal):
    debug('saveMort')
    try:
        mortObj = Threshold_Values.objects.filter(title = "Mortality").first()    
        mortObj.value = threshVal
        mortObj.save()
    except:
        Threshold_Values(
            title   = "Mortality",
            value   = threshVal
        ).save()

    return HttpResponse(status=200)

def saveBioThreshold(request, threshVal):
    debug('bio')
    try:
        bioObj = Threshold_Values.objects.filter(title = "Biosecurity").first()    
        bioObj.value = threshVal
        bioObj.save()
    except:
        Threshold_Values(
            title   = "Biosecurity",
            value   = threshVal
        ).save()

    return HttpResponse(status=200)

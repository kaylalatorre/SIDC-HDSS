# for page redirection, server response
from django import http
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, response

# for storing success and error Django messages
from django.contrib import messages

# for Model imports
from django.contrib.auth.models import User
from farmsapp.models import (
    Farm, Area, Hog_Raiser, Farm_Weight, 
    Mortality, Hog_Symptoms, Mortality_Form, 
    Pigpen_Group, Pigpen_Row, Activity,
    Disease_Case, Disease_Record, SEIRD_Input)

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
        trembling           =F('incid_case__trembling')         ,       conjunctivitis      =F('incid_case__conjunctivitis')
    ).values(
        'incid_case__id'                ,        'incid_case__ref_farm_id'       ,        'incid_case__num_pigs_affected' ,        'lab_result'                    ,        
        'lab_ref_no'                    ,        'high_fever'                    ,        'loss_appetite'                 ,        'depression'                    ,        
        'lethargic'                     ,        'constipation'                  ,        'vomit_diarrhea'                ,        'colored_pigs'                  ,        
        'skin_lesions'                  ,        'hemorrhages'                   ,        'abn_breathing'                 ,        'discharge_eyesnose'            ,        
        'death_isDays'                  ,        'death_isWeek'                  ,        'cough'                         ,        'sneeze'                        ,        
        'runny_nose'                    ,        'waste'                         ,        'boar_dec_libido'               ,        'farrow_miscarriage'            ,        
        'weight_loss'                   ,        'trembling'                     ,        'conjunctivitis'                ,        'disease_name'                  ,
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
        dcurrCase = [key for key, val in dcase.items() if val and key not in ['incid_case__id', 'incid_case__ref_farm_id', 'incid_case__num_pigs_affected', 'lab_result', 'lab_ref_no', 'disease_name']]
        dname = dcase['disease_name']
        
        if dname == 'ASF':
            diseaseInfo['ASF']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no']
                })
            diseaseInfo['ASF']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'CSF':
            diseaseInfo['CSF']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no']
                })
            diseaseInfo['CSF']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'IAVS':
            diseaseInfo['IAVS']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no']
                })
            diseaseInfo['IAVS']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'ADV':
            diseaseInfo['ADV']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no']
                })
            diseaseInfo['ADV']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'PRRS':
            diseaseInfo['PRRS']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no']
                })
            diseaseInfo['PRRS']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'PED':
            diseaseInfo['PED']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no']
                })
            diseaseInfo['PED']['hogs_total'] += dcase['incid_case__num_pigs_affected']

        if dname == 'Others':
            diseaseInfo['Others']['diseaseList'].append({
                'incid_id': dcase['incid_case__id'], 
                'farm_id': dcase['incid_case__ref_farm_id'], 
                'hogs_affect': dcase['incid_case__num_pigs_affected'], 
                'symptoms': dcurrCase,
                'lab_result': dcase['lab_result'], 
                'lab_ref': dcase['lab_ref_no']
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
        diseaase_name = request.POST.get("disease_name")
        incid_id = request.POST.get("incid_id")
        num_pigs_affect = request.POST.get("lab_result")
        date_updated = datetime.now(timezone.utc)
        lab_result = False
        if int(num_pigs_affect) > 0:
            lab_result = True
        
        try:
            # save disease case
            dCase = Disease_Case(
                disease_name    = diseaase_name,
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
                num_died            = total_died,
                ref_disease_case    = dCase,
                total_died          = total_died,
                total_recovered     = 0
            ).save()
            # resolve incident case
            Hog_Symptoms.objects.filter(id=incid_id).update(report_status="Resolved")
            # success response
            return HttpResponse(status=200)
        except:
            # error response
            return HttpResponse(status=500)
            
# rendering disease-monitoring.html in a different url
def diseaseMonitoring(strDisease):


    # Lab Reference	    Incident Involved   	No. of Pigs Affected	Recovered	Died

    data = []
    # debug(request.method)
    print(strDisease)

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

    inputQry = SEIRD_Input.objects.filter(disease_name=strDisease).first()

    # append data to return (table, SEIRD inputs) 
    data.append(dTable)
    data.append(inputQry)
    debug(data)

    return data # for disease monitoring dashboard contents

def load_ConfirmedCases(request, strDisease):
    """
    Used for when calling .load 
    """
    return render(request, 'dsstemp/disease-content.html', {"disData": diseaseMonitoring(strDisease)})

def load_diseaseChart(request, strDisease):

    data = []
    # debug(request.method)
    # debug("loading charts")    

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

    confirmedCtr = 0
    recoveredCtr = 0
    diedCtr      = 0
    case_currDate = 0

    # NULL case      
    try:
        case_currDate = dcasesQry.first().date_filed.date()
    except:
        pass

    if case_currDate != dateMonthsAgo.date():
        # start point of series data
        dChart['confirmed'].append([dateMonthsAgo.date(), 0])
        dChart['recovered'].append([dateMonthsAgo.date(), 0])
        dChart['died'].append([dateMonthsAgo.date(), 0])

    dCaseList = []
    for d in dcasesQry:
        try:
            case_nextDate = d.date_filed.date()
        except:
            continue

        # for confirmed cases
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
    if case_currDate != dateToday.date():
        dChart['confirmed'].append([dateToday.date(), 0])
        dChart['recovered'].append([dateToday.date(), 0])
        dChart['died'].append([dateToday.date(), 0])

    # debug(dChart)

    # append data to return (table, line chart, map, SEIRD) 
    data.append(dChart)
    # debug(data)

    # load_diseaseSeird()

    return JsonResponse(data, safe=False)
    

def actionRecommendation(request):
    return render(request, 'dsstemp/action-rec.html')


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
    debug("SEIRD")
    debug(strDisease)
    # compute for total SIDC pig population
    farmQry = Farm.objects.aggregate(Sum("total_pigs"))
    N = farmQry["total_pigs__sum"]

    # get initial parameters from frontend inputs
    sValues = []
    sValues = request.POST.getlist("values[]")
    if sValues:
        sParam = [int(sValues[0]), float(sValues[1]), int(sValues[2]), float(sValues[3]), int(sValues[4])]
        debug(sParam)
    else:
        params = SEIRD_Input.objects.filter(disease_name=strDisease).first()
        sParam = [
            params.incub_days,
            params.reproduction_num,
            params.days_can_spread,
            params.fatality_rate,
            params.days_til_death
        ]

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
    S, E, I, R, D = retVal.T

    # debug(retVal)
    # debug(E)
    totalPigs = [int(farmQry["total_pigs__sum"]) for i in S.tolist()]
    modelData = [totalPigs, S.tolist(), E.tolist(), I.tolist(), R.tolist(), D.tolist()]
    return JsonResponse(modelData, safe=False)

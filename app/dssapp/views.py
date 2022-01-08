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
    Pigpen_Group, Pigpen_Row)

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
    incidQry = Hog_Symptoms.objects.select_related('ref_farm').annotate(
        farm_code = F("ref_farm__id"),
        farm_area = F("ref_farm__area__area_name"),
        ).values(
            "id",
            "farm_code",
            "farm_area",
            "num_pigs_affected",
            "report_status",
            "date_filed"
            ).order_by("id")

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
    symptomsList = Hog_Symptoms.objects.values(
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
            'conjunctivitis').order_by("id").all()

    sDiseaseList = []
    for sRow in symptomsList:
        dList = checkDiseaseList(sRow)
        sDiseaseList.append(dList)
        # debug(sDiseaseList)
    

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidList, symptomsList, sDiseaseList)

    return render(request, 'dsstemp/rep-disease-monitoring.html', {"isFiltered": isFiltered, 'dateStart': dateToday,'dateEnd': dateToday,
                                                                    "areaList": areaQry,
                                                                    "incident_symptomsList": incident_symptomsList,
                                                                    "total_pigs_affect": total_pigs_affect})

def filter_incidentRep(request, startDate, endDate, areaName):
    debug("TEST LOG: in filter_mortalityRep/n")

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
        debug("TRACE: in areaName == 'All'")

        # (3.1) Incident details
        incidQry = Hog_Symptoms.objects.filter(date_filed__range=(sDate, eDate)).select_related('ref_farm').annotate(
            farm_code = F("ref_farm__id"),
            farm_area = F("ref_farm__area__area_name"),
            ).values(
                "id",
                "farm_code",
                "farm_area",
                "num_pigs_affected",
                "report_status",
                "date_filed"
                ).order_by("id")


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
        symptomsList = Hog_Symptoms.objects.filter(date_filed__range=(sDate, eDate)).values(
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
                'conjunctivitis').order_by("id").all()
        

    else: # (CASE 2) search by BOTH date range and areaName
        debug("TRACE: in else/")

        incidQry = Hog_Symptoms.objects.filter(date_filed__range=(sDate, eDate)).filter(ref_farm__area__area_name=areaName).select_related('ref_farm').annotate(
            farm_code = F("ref_farm__id"),
            farm_area = F("ref_farm__area__area_name"),
            ).values(
                "id",
                "farm_code",
                "farm_area",
                "num_pigs_affected",
                "report_status",
                "date_filed"
                ).order_by("id")

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
        symptomsList = Hog_Symptoms.objects.filter(date_filed__range=(sDate, eDate)).filter(ref_farm__area__area_name=areaName).values(
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
                'conjunctivitis').order_by("id").all()
        

    sDiseaseList = []
    for sRow in symptomsList:
        dList = checkDiseaseList(sRow)
        sDiseaseList.append(dList)
        # debug(sDiseaseList)

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidList, symptomsList, sDiseaseList)


    return render(request, 'dsstemp/rep-disease-monitoring.html', {"isFiltered": isFiltered, 'dateStart': sDate,'dateEnd': truEndDate,
                                                                    "areaList": areaQry, 
                                                                    "incident_symptomsList": incident_symptomsList,
                                                                    "total_pigs_affect": total_pigs_affect})

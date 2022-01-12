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
    # total_symptoms = 0
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
    

    # combine the 2 previous queries into 1 temporary list
    incident_symptomsList = zip(incidList, symptomsList)

    return render(request, 'dsstemp/rep-disease-monitoring.html', {"isFiltered": isFiltered, 'dateStart': dateToday,'dateEnd': dateToday,
                                                                    "areaList": areaQry,
                                                                    "incident_symptomsList": incident_symptomsList})

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
            diseaseInfo['ASF']['symptoms'].extend(
                list(set(diseaseInfo['ADV']['symptoms'])-set(diseaseSymptoms['ADV']).intersection(currCase)) + 
                list(set(diseaseSymptoms['ADV']).intersection(currCase)-set(diseaseInfo['ADV']['symptoms']))
            )
        if len(list(set(diseaseSymptoms['PRRS'])-set(currCase))) == 0:
            if case['ref_farm_id'] not in diseaseInfo['PRRS']['farms']:
                diseaseInfo['PRRS']['farms'].append(case['ref_farm_id'])
            diseaseInfo['PRRS']['hogs'] += case['num_pigs_affected']
            diseaseInfo['ASF']['symptoms'].extend(
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
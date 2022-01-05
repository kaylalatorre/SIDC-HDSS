from django.urls import path
from . import views

# Farms Management Module URLS

urlpatterns = [
    # for asst. manager view
    path('hogs-health', views.hogsHealth, name="hogsHealth"),
    path('selected-hogs-health/<str:farmID>', views.selectedHogsHealth, name="selectedHogsHealth"),
    path('selected-hogs-health/<str:farmID>/<str:farmVersion>', views.selectedHogsHealthVersion, name="selectedHogsHealthVersion"),

    # reports (asm view)
    path('hogs-mortality', views.hogsMortality, name="hogsMortality"),
    path('hogs-mortality/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_mortalityRep, name="filter_mortalityRep"),
    path('incidents-reported', views.incidentsReported, name="incidentsReported"),
    # path('incidents-reported/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_incidentRep, name="filter_incidentRep"),


    # for technician view
    path('health-symptoms', views.healthSymptoms, name="healthSymptoms"),
    path('selected-health-symptoms/<str:farmID>', views.selectedHealthSymptoms, name="selectedHealthSymptoms"),
    path('selected-health-symptoms/<str:farmID>/<str:farmVersion>', views.selectedHealthSymptomsVersion, name="selectedHealthSymptomsVersion"),
    path('update-incident-status/<str:incidID>', views.edit_incidStat, name="editIncidentStat"),

    # technician - case and mortality record
    path('add-case/<str:farmID>', views.addCase, name="addCase"),
    path('post-addCase/<str:farmID>', views.post_addCase, name="post-addCase"),
    path('add-mortality/<str:farmID>', views.addMortality, name="addMortality"),
    path('save-mortality/<str:farmID>/<str:mortalityID>', views.saveMortality, name="saveMortality"),
    # path('delete-activity/<str:mortalityID>', views.deleteMortality, name="deleteMortality"),

    # forms
    path('selected-mortality-form/<str:mortalityFormID>/<str:mortalityDate>', views.selectedMortalityForm, name="selectedMortalityForm"),
    path('approve-mortality-form/<str:mortalityFormID>', views.approveMortalityForm, name="approveMortalityForm"),
    path('reject-mortality-form/<str:mortalityFormID>', views.rejectMortalityForm, name="rejectMortalityForm"),
    path('resubmit-mortality-form/<str:mortalityFormID>/<str:farmID>/<str:mortalityDate>', views.resubmitMortalityForm, name="resubmitMortalityForm"),

    path('add-weight', views.addWeight, name="addWeight"),
]
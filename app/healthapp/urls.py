from django.urls import path
from . import views

# Farms Management Module URLS

urlpatterns = [
    # for asst. manager view
    path('hogs-health', views.hogsHealth, name="hogsHealth"),
    path('selected-hogs-health/<str:farmID>', views.selectedHogsHealth, name="selectedHogsHealth"),

    path('hogs-mortality', views.hogsMortality, name="hogsMortality"),
    path('incidents-reported', views.incidentsReported, name="incidentsReported"),

    # for technician view
    path('health-symptoms', views.healthSymptoms, name="healthSymptoms"),
    path('selected-health-symptoms/<str:farmID>', views.selectedHealthSymptoms, name="selectedHealthSymptoms"),
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

]
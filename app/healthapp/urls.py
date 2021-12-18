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

    path('add-case', views.addCase, name="addCase"),
    path('add-incident-case', views.post_addCase, name="post-addCase")
    
    path('add-mortality', views.addMortality, name="addMortality"),
]
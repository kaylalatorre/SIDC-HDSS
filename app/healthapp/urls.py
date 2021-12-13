from django.urls import path
from . import views

# Farms Management Module URLS

urlpatterns = [
    path('hogs-health', views.hogsHealth, name="hogsHealth"),
    path('selected-hogs-health', views.selectedHogsHealth, name="selectedHogsHealth"),
    path('hogs-mortality', views.hogsMortality, name="hogsMortality"),
    path('incidents-reported', views.incidentsReported, name="incidentsReported"),
    path('health-symptoms', views.healthSymptoms, name="healthSymptoms"),
    path('selected-health-symptoms', views.selectedHealthSymptoms, name="selectedHealthSymptoms"),
    path('add-case', views.addCase, name="addCase"),
    path('add-mortality', views.addMortality, name="addMortality"),
]
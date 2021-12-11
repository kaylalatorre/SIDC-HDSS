from django.urls import path
from . import views

# Farms Management Module URLS

urlpatterns = [
    # for asst. manager view
    path('hogs-health', views.hogsHealth, name="hogsHealth"),
    path('selected-hogs-health/<str:farmID>', views.selectedHogsHealth, name="selectedHogsHealth"),

    path('hogs-mortality', views.hogsMortality, name="hogsMortality"),
    path('symptoms-reported', views.symptomsReported, name="symptomsReported"),

    # for technician view
    path('health-symptoms', views.healthSymptoms, name="healthSymptoms"),
    path('selected-health-symptoms/<str:farmID>', views.selectedHealthSymptoms, name="selectedHealthSymptoms"),
    path('add-case', views.addCase, name="addCase"),
]
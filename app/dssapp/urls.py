from django.urls import path
from . import views

# Disease Monitoring Module URLS

urlpatterns = [
    # dashboard - symptoms monitoring
    path('submit-lab-report/<int:lab_ref>', views.submitLabReport, name="submitLabReport"),

    # dashboard - disease monitoring
    path('disease-dashboard', views.diseaseDashboard, name="diseaseDashboard"),
    
    # action rec
    path('action-recommendation', views.actionRecommendation, name="actionRecommendation"),
    path('saveThreshold/mortality/<int:threshVal>', views.saveMortThreshold, name="saveMortThreshold"),
    path('saveThreshold/biosecurity/<int:threshVal>', views.saveBioThreshold, name="saveBioThreshold"),
    
    # reports
    path('disease-monitoring/<str:strDisease>/', views.load_diseaseMonitoring, name="diseaseMonitoring"),
    path('load-confirmed-cases/<strDisease>/', views.load_ConfirmedCases, name="loadConfirmedCases"),
    path('symptoms-monitoring', views.symptomsMonitoring, name="symptomsMonitoring"),
    path('symptoms-monitoring/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_incidentRep, name="filter_incidentRep"),

    # charts
    path('disease-chart/<str:strDisease>/', views.load_diseaseChart, name="load_diseaseChart"),
    path('disease-seird/<str:strDisease>/', views.load_diseaseSeird, name="load_diseaseSeird"),

    # map
    path('disease-map/<str:strDisease>', views.load_diseaseMap, name="load_diseaseMap"),
]
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
    
    # reports
    path('disease-monitoring', views.diseaseMonitoring, name="diseaseMonitoring"),
    path('symptoms-monitoring', views.symptomsMonitoring, name="symptomsMonitoring"),
    path('symptoms-monitoring/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_incidentRep, name="filter_incidentRep"),
]
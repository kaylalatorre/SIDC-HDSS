from django.urls import path
from . import views

# Disease Monitoring Module URLS

urlpatterns = [
    # dashboard - symptoms monitoring
    path('submit-lab-report/<int:lab_ref>', views.submitLabReport, name="submitLabReport"),

    # dashboard - disease monitoring
    path('disease-dashboard', views.diseaseDashboard, name="diseaseDashboard"),
    
    # reports
    path('disease-monitoring', views.diseaseMonitoring, name="diseaseMonitoring"),
    path('disease-monitoring/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_incidentRep, name="filter_incidentRep"),
]
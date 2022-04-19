from django.urls import path
from . import views

# Disease Monitoring Module URLS

urlpatterns = [
    # dashboard
    path('disease-dashboard', views.diseaseDashboard, name="diseaseDashboard"),
    
    # action rec
    path('action-recommendation', views.actionRecommendation, name="actionRecommendation"),
    
    # reports
    path('symptoms-monitoring', views.symptomsMonitoring, name="symptomsMonitoring"),
    path('symptoms-monitoring/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_incidentRep, name="filter_incidentRep"),
]
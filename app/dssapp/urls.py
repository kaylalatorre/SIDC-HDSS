from django.urls import path
from . import views

# Disease Monitoring Module URLS

urlpatterns = [
    # reports
    path('disease-monitoring', views.diseaseMonitoring, name="diseaseMonitoring"),
    path('disease-monitoring/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_incidentRep, name="filter_incidentRep"),

]
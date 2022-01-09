from django.urls import path
from . import views

# Disease Monitoring Module URLS

urlpatterns = [
    # dashboard - disease monitoring
    path('disease-dashboard', views.diseaseDashboard, name="diseaseDashboard"),
    
    # reports
    path('disease-monitoring', views.diseaseMonitoring, name="diseaseMonitoring"),
]
from django.urls import path
from . import views

# Disease Monitoring Module URLS

urlpatterns = [
    # reports
    path('disease-monitoring', views.diseaseMonitoring, name="diseaseMonitoring"),

]
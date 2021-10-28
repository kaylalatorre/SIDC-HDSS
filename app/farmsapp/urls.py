from django.urls import path
from . import views

# Farms Management Module URLS

urlpatterns = [
    path('farms', views.farms, name="farms"),
    path('add-farm', views.addFarm, name="addFarm"),
]
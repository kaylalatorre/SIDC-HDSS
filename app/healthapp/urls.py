from django.urls import path
from . import views

# Farms Management Module URLS

urlpatterns = [
    path('hogs-health', views.hogsHealth, name="hogsHealth"),
    path('selected-hogs-health', views.selectedHogsHealth, name="selectedHogsHealth"),
]
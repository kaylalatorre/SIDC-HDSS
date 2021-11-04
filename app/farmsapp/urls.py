from django.urls import path
from . import views

# Farms Management Module URLS

urlpatterns = [
    path('', views.home, name="home"),
    path('home', views.home, name="home"),
    path('farms', views.farms, name="farms"),
    path('add-farm', views.addFarm, name="addFarm"),
    path('save-farm', views.saveFarm, name="saveFarm"),
    path('biosecurity', views.biosec_view, name="biosecurity"),

    path('add-checklist', views.addChecklist, name="addChecklist"),
    path('post-addchecklist', views.post_addChecklist, name="post-addChecklist"),

    path('add-activity', views.addActivity, name="addActivity"),
]
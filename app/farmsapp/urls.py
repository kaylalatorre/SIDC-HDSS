from django.urls import path
from . import views

# Farms Management Module URLS

urlpatterns = [
    path('farms', views.farms, name="farms"),
    path('add-farm', views.addFarm, name="addFarm"),

    path('biosecurity', views.biosec_view, name="biosecurity"),
    path('biosecurity/getchecklist', views.search_bioChecklist, name="search_biochecklist"),
    path('add-checklist', views.addChecklist, name="addChecklist"),
    path('post-addchecklist', views.post_addChecklist, name="post-addChecklist"),

    path('add-activity', views.addActivity, name="addActivity"),
]
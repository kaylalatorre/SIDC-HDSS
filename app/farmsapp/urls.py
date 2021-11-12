from django.urls import path
from . import views

# Farms Management Module URLS

urlpatterns = [
    path('farms', views.farms, name="farms"),
    path('selected-farm', views.selectedFarm, name="selectedFarm"),
    path('add-farm', views.addFarm, name="addFarm"),
    
    path('tech-selected-farm', views.techSelectedFarm, name="techSelectedFarm"),
    path('technician-assignment', views.techAssignment, name="techAssignment"),
    path('forms-approval', views.formsApproval, name="formsApproval"),
    path('selected-form', views.selectedForm, name="selectedForm"),

    # for biosecurity
    path('biosecurity', views.biosec_view, name="biosecurity"),
    path('biosecurity/getchecklist', views.search_bioChecklist, name="search_biochecklist"),
    path('biosecurity/updatechecklist', views.update_bioChecklist, name="update_biochecklist"),
    path('add-checklist', views.addChecklist_view, name="addChecklist"),
    path('post-addchecklist', views.post_addChecklist, name="post-addChecklist"),

    path('add-activity', views.addActivity, name="addActivity"),
    path('member-announcements', views.memAnnouncements, name="memAnnouncements"),
    path('create-announcement', views.createAnnouncement, name="createAnnouncement"),
    path('view-announcement', views.viewAnnouncement, name="viewAnnouncement"),

    # reports
    path('farms-assessment', views.farmsAssessment, name="farmsAssessment"),
    path('int-biosecurity', views.intBiosecurity, name="intBiosecurity"),
    path('ext-biosecurity', views.extBiosecurity, name="extBiosecurity"),
]
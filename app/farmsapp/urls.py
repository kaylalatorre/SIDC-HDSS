from django.urls import path, re_path
from . import views

# Farms Management Module URLS
# r'^selected-farm/(?P<parameter>[0-9]+)$'
urlpatterns = [

    # asst. manager - view farms
    path('farms', views.farms, name="farms"),
    path('selected-farm/<str:farmID>', views.selectedFarm, name="selectedFarm"),

    # asst. manager - assign technicians
    path('technician-assignment', views.techAssignment, name="techAssignment"),
    path('technician-assignment/assign', views.assign_technician, name="assign_technician"),

    # asst. manager - forms
    path('forms-approval', views.formsApproval, name="formsApproval"),
    path('selected-form', views.selectedForm, name="selectedForm"),
    
    # technician - view and add farms
    path('add-farm', views.addFarm, name="addFarm"),
    path('tech-farms', views.techFarms, name="techFarms"),
    path('home/view-farm', views.techFarms, name="techFarms"),
    path('tech-selected-farm/<str:farmID>', views.techSelectedFarm, name="techSelectedFarm"),

    # technician - biosecurity
    path('biosecurity', views.biosec_view, name="biosecurity"),
    path('biosecurity/<str:farmID>', views.select_biosec, name="select_biosecurity"),

    # technician - biosecurity checklist
    path('biosecurity/getchecklist/<str:biosecID>', views.search_bioChecklist, name="search_biochecklist"),
    path('biosecurity/edit-checklist/<str:biosecID>', views.update_bioChecklist, name="update_biochecklist"),
    path('biosecurity/delete-checklist/<str:biosecID>', views.delete_bioChecklist, name="delete_biochecklist"),
    path('add-checklist/<str:farmID>', views.addChecklist_view, name="addChecklist"),
    path('post-addchecklist/<str:farmID>', views.post_addChecklist, name="post-addChecklist"), # not working even without param

    # technician - biosecurityactivity
    path('add-activity/<str:farmID>', views.addActivity, name="addActivity"),

    # announcements
    path('member-announcements', views.memAnnouncements, name="memAnnouncements"),
    path('create-announcement', views.createAnnouncement, name="createAnnouncement"),
    path('view-announcement', views.viewAnnouncement, name="viewAnnouncement"),

    # reports
    path('farms-assessment', views.farmsAssessment, name="farmsAssessment"),
    path('int-biosecurity', views.intBiosecurity, name="intBiosecurity"),
    path('ext-biosecurity', views.extBiosecurity, name="extBiosecurity"),
]
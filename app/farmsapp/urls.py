from django.urls import path, re_path
from . import views

# Farms Management Module URLS
# r'^selected-farm/(?P<parameter>[0-9]+)$'
urlpatterns = [
    # Map
    path('map-data', views.getMapData, name="getMapData"),

    # asst. manager - view farms
    path('farms', views.farms, name="farms"),
    path('selected-farm/<str:farmID>', views.selectedFarm, name="selectedFarm"),
    path('selected-farm/<str:farmID>/<str:farmVersion>', views.selectedFarmVersion, name="selectedFarmVersion"),

    # asst. manager - assign technicians
    path('technician-assignment', views.techAssignment, name="techAssignment"),
    path('technician-assignment/assign', views.assign_technician, name="assign_technician"),
    path('technician-assignment/savearea', views.save_area, name="save_area"),
    path('technician-assignment/search-tasks/<str:techID>', views.search_techTasks, name="search_techTasks"),


    # forms
    path('forms-approval', views.formsApproval, name="formsApproval"),
    path('selected-activity-form/<str:activityFormID>/<str:activityDate>', views.selectedActivityForm, name="selectedActivityForm"),
    path('approve-activity-form/<str:activityFormID>', views.approveActivityForm, name="approveActivityForm"),
    path('reject-activity-form/<str:activityFormID>', views.rejectActivityForm, name="rejectActivityForm"),
    path('resubmit-activity-form/<str:activityFormID>/<str:farmID>/<str:activityDate>', views.resubmitActivityForm, name="resubmitActivityForm"),
    
    # technician - view and add farms
    path('add-farm', views.addFarm, name="addFarm"),
    path('home/tech-farms', views.techFarms, name="techFarms"),
    path('tech-selected-farm/<str:farmID>', views.techSelectedFarm, name="techSelectedFarm"),
    path('tech-selected-farm/<str:farmID>/<str:farmVersion>', views.techSelectedFarmVersion, name="techSelectedFarmVersion"),

    # technician - biosecurity
    path('biosecurity', views.biosec_view, name="biosecurity"),
    path('biosecurity/<str:farmID>', views.select_biosec, name="select_biosecurity"),

    # technician - biosecurity checklist
    path('biosecurity/getchecklist/<str:biosecID>', views.search_bioChecklist, name="search_biochecklist"),
    path('biosecurity/edit-checklist/<str:biosecID>', views.update_bioChecklist, name="update_biochecklist"),
    path('biosecurity/delete-checklist/<str:biosecID>/<str:farmID>', views.delete_bioChecklist, name="delete_biochecklist"),
    path('add-checklist/<str:farmID>', views.addChecklist_view, name="addChecklist"),
    path('post-addchecklist/<str:farmID>', views.post_addChecklist, name="post-addChecklist"), # not working even without param

    # technician - biosecurity activity
    path('add-activity/<str:farmID>', views.addActivity, name="addActivity"),
    path('save-activity/<str:farmID>/<str:activityID>', views.saveActivity, name="saveActivity"),
    path('delete-activity/<str:activityID>', views.deleteActivity, name="deleteActivity"),

    # announcements
    path('member-announcements', views.memAnnouncements, name="memAnnouncements"),
    path('member-announcements/<str:decision>', views.memAnnouncements_Approval, name="memAnnouncements_Approval"),
    path('create-announcement', views.createAnnouncement, name="createAnnouncement"),
    path('view-announcement/<int:id>', views.viewAnnouncement, name="viewAnnouncement"),
    path('resubmit-announcement/<int:id>', views.viewAnnouncement, name="resubmitAnnouncement"),

    # notifications
    path('notifications', views.getNotifications, name='getNotifications'),
    path('notifications/count', views.countNotifications, name='countNotifications'),
    path ('notifications/sync', views.syncNotifications, name='syncNotifications'),

    # reports
    path('farms-assessment', views.farmsAssessment, name="farmsAssessment"),
    path('farms-assessment/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_farmsAssessment, name="filter_farmsAssessment"),

    path('int-biosecurity', views.intBiosecurity, name="intBiosecurity"),
    path('int-biosecurity/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_intBiosec, name="filter_intBiosec"),

    path('ext-biosecurity', views.extBiosecurity, name="extBiosecurity"),
    path('ext-biosecurity/<str:startDate>/<str:endDate>/<str:areaName>/', views.filter_extBiosec, name="filter_extBiosec"),

    # asst. manager - farm detail dashboard
    path('home/dash', views.dashboard_view, name="dashboard-view"),

]
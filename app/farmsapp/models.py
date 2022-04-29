from typing_extensions import ParamSpec
from django.db import models
from django.utils.timezone import now 

# for importing Users
from django.contrib.auth.models import User

# for importing Users from
from django.conf import settings


class User(User):
    pass

class AccountData(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    data = models.JSONField(default=dict, null=True)

    def __str__(self):
        return self.id


# EXTERNAL BIOSEC Table
class ExternalBiosec(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)
    last_updated        = models.DateTimeField(auto_now=True, editable=True)

    # fields from Biomeasures
    bird_proof          = models.IntegerField(null=True, blank=True, default=1)
    perim_fence         = models.IntegerField(null=True, blank=True, default=1)
    fiveh_m_dist        = models.IntegerField(null=True, blank=True, default=1)
    
    # fields from Biochecklist
    prvdd_foot_dip      = models.IntegerField(null=True, blank=True)
    prvdd_alco_soap     = models.IntegerField(null=True, blank=True)
    obs_no_visitors     = models.IntegerField(null=True, blank=True)
    prsnl_dip_footwear  = models.IntegerField(null=True, blank=True)
    prsnl_sanit_hands   = models.IntegerField(null=True, blank=True)
    chg_disinfect_daily = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.id


# INTERNAL BIOSEC Table
class InternalBiosec(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)
    last_updated        = models.DateTimeField(auto_now=True, editable=True)
    
    # fields from Biomeasures
    isol_pen            = models.IntegerField(null=True, blank=True, default=1)
    foot_dip            = models.IntegerField(null=True, blank=True, default=1)
    waste_mgt           = models.CharField(null=True, blank=True, max_length=50)
    
    # fields from Biochecklist
    disinfect_prem      = models.IntegerField(null=True, blank=True)
    disinfect_vet_supp  = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.id


# FARM WEIGHT Table
class Farm_Weight(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)

    date_filed          = models.DateField(default=now)
    is_starter          = models.BooleanField(default=False)
    ave_weight          = models.FloatField()
    total_numHeads      = models.IntegerField()
    total_kls           = models.FloatField()
    remarks             = models.CharField(max_length=200, null=True, blank=True)


# INVIDUAL HOG FINAL WEIGHT
class Hog_Weight(models.Model):
    farm_weight         = models.ForeignKey('Farm_Weight', on_delete=models.CASCADE, related_name='+', null=True, blank=True)

    final_weight        = models.FloatField()
    

# HOG SYMPTOMS Table
class Hog_Symptoms(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)
    pigpen_grp          = models.ForeignKey('Pigpen_Group', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)

    date_filed          = models.DateTimeField(default=now)
    date_updated        = models.DateTimeField(auto_now=True, editable=True)

    report_status       = models.CharField(max_length=50, default='Active')
    num_pigs_affected   = models.IntegerField(default=0)

    high_fever          = models.BooleanField(default=False, null=True, blank=True)
    loss_appetite       = models.BooleanField(default=False, null=True, blank=True)
    depression          = models.BooleanField(default=False, null=True, blank=True)
    lethargic           = models.BooleanField(default=False, null=True, blank=True)
    constipation        = models.BooleanField(default=False, null=True, blank=True)
    vomit_diarrhea      = models.BooleanField(default=False, null=True, blank=True)
    colored_pigs        = models.BooleanField(default=False, null=True, blank=True)
    skin_lesions        = models.BooleanField(default=False, null=True, blank=True)
    hemorrhages         = models.BooleanField(default=False, null=True, blank=True)
    abn_breathing       = models.BooleanField(default=False, null=True, blank=True)
    discharge_eyesnose  = models.BooleanField(default=False, null=True, blank=True)
    death_isDays        = models.BooleanField(default=False, null=True, blank=True)
    death_isWeek        = models.BooleanField(default=False, null=True, blank=True)
    cough               = models.BooleanField(default=False, null=True, blank=True)
    sneeze              = models.BooleanField(default=False, null=True, blank=True)
    runny_nose          = models.BooleanField(default=False, null=True, blank=True)
    waste               = models.BooleanField(default=False, null=True, blank=True)
    boar_dec_libido     = models.BooleanField(default=False, null=True, blank=True)
    farrow_miscarriage  = models.BooleanField(default=False, null=True, blank=True)
    weight_loss         = models.BooleanField(default=False, null=True, blank=True)
    trembling           = models.BooleanField(default=False, null=True, blank=True)
    conjunctivitis      = models.BooleanField(default=False, null=True, blank=True)

    others              = models.JSONField(default=dict, null=True)
    remarks             = models.CharField(max_length=200, null=True, blank=True)


# DISEASE CASE Table
class Disease_Case(models.Model):
    disease_name        = models.CharField(max_length=100)

    lab_result          = models.BooleanField(null=True, blank=True)
    lab_ref_no          = models.IntegerField(null=True, blank=True)

    date_updated        = models.DateTimeField(auto_now=True, editable=True)
    start_date          = models.DateTimeField(null=True, blank=True)
    end_date            = models.DateTimeField(null=True, blank=True)

    incid_case          = models.ForeignKey('Hog_Symptoms', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)

    num_pigs_affect     = models.IntegerField(null=True, blank=True)

# DISEASE RECORD Table
class Disease_Record(models.Model):
    date_filed          = models.DateField(default=now)

    num_recovered       = models.IntegerField(null=True, blank=True)
    num_died            = models.IntegerField(null=True, blank=True)

    ref_disease_case    = models.ForeignKey('Disease_Case', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)

    total_died          = models.IntegerField(null=True, blank=True)
    total_recovered     = models.IntegerField(null=True, blank=True)

# HOG RAISER Table
class Hog_Raiser(models.Model):
    mem_code            = models.IntegerField(null=True, blank=True)
    fname               = models.CharField(max_length=50)
    lname               = models.CharField(max_length=50)
    contact_no          = models.CharField(max_length=12)
    mem_code            = models.IntegerField(null=True, unique=True)


# AREA Table
class Area(models.Model):
    area_name           = models.CharField(max_length=20, null=True, blank=True)
    tech                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='tech', null=True, blank=True)


# FARM Table
class Farm(models.Model): 
    hog_raiser          = models.ForeignKey('Hog_Raiser', on_delete=models.SET_NULL, null=True, blank=True)
    directly_manage     = models.BooleanField(default=False)

    date_registered     = models.DateField(default=now, null=True, blank=True)
    last_updated        = models.DateTimeField(auto_now=True, editable=True)

    area                = models.ForeignKey('Area', related_name="area", on_delete=models.SET_NULL, null=True, blank=True)
    farm_address        = models.CharField(max_length=200, null=True, blank=True)
    loc_long            = models.FloatField(null=True, blank=True)
    loc_lat             = models.FloatField(null=True, blank=True)

    roof_height         = models.FloatField()
    wh_length           = models.FloatField()
    wh_width            = models.FloatField()   
    
    FEED_CHOICES        = [('Semi-automatic', 'Semi-automatic'),
                            ('Trough', 'Trough')]

    feed_trough         = models.CharField(max_length=20, choices=FEED_CHOICES, default='Semi-automatic')
    bldg_cap            = models.IntegerField()

    MED_TANK_CHOICES    = [('25 GAL', '25 GAL'),
                            ('50 GAL', '50 GAL')]

    medic_tank          = models.CharField(max_length=10, choices=MED_TANK_CHOICES, default='25 GAL')
    bldg_curtain        = models.BooleanField(default=False)
    road_access         = models.BooleanField(default=False)

    num_pens            = models.IntegerField(null=True, blank=True)
    total_pigs          = models.IntegerField(null=True, blank=True)
    
    extbio              = models.ForeignKey('ExternalBiosec', on_delete=models.SET_NULL, null=True, blank=True)
    intbio              = models.ForeignKey('InternalBiosec', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.id


# PIGPEN_GROUP TABLE
class Pigpen_Group(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)
    date_added          = models.DateField(default=now, editable=False)

    num_pens            = models.IntegerField(null=True, blank=True)
    total_pigs          = models.IntegerField(null=True, blank=True)

    start_weight        = models.ForeignKey('Farm_Weight', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)
    final_weight        = models.ForeignKey('Farm_Weight', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)


# PIGPEN MEASURES Table
class Pigpen_Row(models.Model):
    pigpen_grp          = models.ForeignKey('Pigpen_Group', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)

    length              = models.FloatField()
    width               = models.FloatField()
    num_heads           = models.IntegerField()


# ACTIVITY Table
class Activity(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)

    date                = models.DateField()

    TYPE_CHOICES        = [('Delivery of Veterinary Supplies', 'Delivery of Veterinary Supplies'),
                            ('Delivery of Medicine', 'Delivery of Medicine'),
                            ('Monthly Inventory', 'Monthly Inventory'),
                            ('Blood Collection', 'Blood Collection'),
                            ('Vaccinations', 'Vaccinations'),
                            ('Inspection', 'Inspection'),
                            ('Sold Pigs', 'Sold Pigs'),
                            ('Other', 'Other')]

    trip_type           = models.CharField(max_length=50, choices=TYPE_CHOICES)
    time_arrival        = models.TimeField()
    time_departure      = models.TimeField()
    num_pigs_inv        = models.IntegerField(null=True, blank=True)
    remarks             = models.CharField(max_length=200, null=True, blank=True)

    last_updated        = models.DateTimeField(auto_now=True, editable=True)
    date_approved       = models.DateTimeField(null=True, blank=True)

    is_approved         = models.BooleanField(null=True, editable=True)

    activity_form       = models.ForeignKey('Activities_Form', on_delete=models.CASCADE, related_name='+', null=True, blank=True)


# ACTIVITIES FORM Table
class Activities_Form(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)

    code                = models.IntegerField(null=True, blank=True)
    is_latest           = models.BooleanField(null=True, editable=True)
    date_added          = models.DateField(null=True, blank=True)

    act_tech            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='act_tech', null=True, blank=True)
    act_liveop          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='act_liveop', null=True, blank=True)
    is_checked          = models.BooleanField(null=True, editable=True)

    reject_reason       = models.CharField(max_length=500, null=True, blank=True)


# MORTALITY Table
class Mortality(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)        

    mortality_date      = models.DateField()
    num_begInv          = models.IntegerField(null=True, blank=True)
    num_today           = models.IntegerField()
    num_toDate          = models.IntegerField(null=True, blank=True)
    
    SOURCE_CHOICES      = [('Incident Case', 'Incident Case'),
                            ('Disease Case', 'Disease Case'),
                            ('Unknown', 'Unknown')]
    
    source              = models.CharField(null=True, blank=True, max_length=50, choices=SOURCE_CHOICES)
    case_no             = models.IntegerField(null=True, blank=True)
    remarks             = models.CharField(max_length=200, null=True, blank=True)

    mortality_form      = models.ForeignKey('Mortality_Form', on_delete=models.CASCADE, related_name='+', null=True, blank=True)


# MORTALITY FORM Table
class Mortality_Form(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)
    pigpen_grp          = models.ForeignKey('Pigpen_Group', on_delete=models.SET_NULL, related_name='+', null=True, blank=True)
    
    series              = models.IntegerField(null=True, blank=True)
    date_added          = models.DateField(null=True, blank=True)


# MEMBER ANNOUNCEMENT Table
class Mem_Announcement(models.Model):
    title               = models.CharField(max_length=150)
    category            = models.CharField(max_length=50)
    recip_area          = models.CharField(max_length=20)
    mssg                = models.CharField(max_length=500)
    author              = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='author', null=True, blank=True)
    timestamp           = models.DateTimeField(default=now)

    is_approved         = models.BooleanField(default=False, null=True)
    reject_reason       = models.CharField(max_length=500, null=True, blank=True)
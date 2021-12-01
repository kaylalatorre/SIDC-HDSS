from typing_extensions import ParamSpec
from django.db import models
from django.utils.timezone import now 

# for importing Users
from django.contrib.auth.models import User
from django.conf import settings

# for importing Users from
from django.conf import settings

class User(User):
    pass

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

    WASTE_MGT_CHOICES   = [('Septic Tank', 'Septic Tank'),
                            ('Biogas', 'Biogas'),
                            ('Other', 'Other')]

    waste_mgt           = models.CharField(max_length=50, choices=WASTE_MGT_CHOICES, default='Septic Tank')
    
    # fields from Biochecklist
    disinfect_prem      = models.IntegerField(null=True, blank=True)
    disinfect_vet_supp  = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.id

# FARM WEIGHT Table
class Farm_Weight(models.Model):
    date_filed          = models.DateField(default=now)
    is_starter          = models.BooleanField(default=False)
    ave_weight          = models.FloatField()
    total_numHeads      = models.IntegerField()
    total_kls           = models.FloatField()

    # def __str__(self):
    #     return self.id

# FARM SYMPTOMS Table
class Hog_Symptoms(models.Model):
    date_filed          = models.DateTimeField(default=now)

    high_fever          = models.BooleanField(default=False)
    loss_appetite       = models.BooleanField(default=False)
    depression          = models.BooleanField(default=False)
    lethargic           = models.BooleanField(default=False)
    constipation        = models.BooleanField(default=False)
    vomit_diarrhea      = models.BooleanField(default=False)
    colored_pigs        = models.BooleanField(default=False)
    skin_lesions        = models.BooleanField(default=False)
    hemorrhages         = models.BooleanField(default=False)
    abn_breathing       = models.BooleanField(default=False)
    discharge_eyesnose  = models.BooleanField(default=False)
    death_isDays        = models.BooleanField(default=False)
    death_isWeek        = models.BooleanField(default=False)
    cough               = models.BooleanField(default=False)
    sneeze              = models.BooleanField(default=False)
    runny_nose          = models.BooleanField(default=False)
    waste               = models.BooleanField(default=False)
    boar_dec_libido     = models.BooleanField(default=False)
    farrow_miscarriage  = models.BooleanField(default=False)
    weight_loss         = models.BooleanField(default=False)
    trembling           = models.BooleanField(default=False)
    conjunctivitis      = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.id

# HOG RAISER Table
class Hog_Raiser(models.Model):
    fname               = models.CharField(max_length=50)
    lname               = models.CharField(max_length=50)
    contact_no          = models.CharField(max_length=15)

    # def __str__(self)
    #     return self.

# AREA Table
class Area(models.Model):
    area_name           = models.CharField(max_length=20, null=True, blank=True)
    tech                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tech', null=True, blank=True)

# FARM Table
class Farm(models.Model): 
    hog_raiser          = models.ForeignKey('Hog_Raiser', on_delete=models.CASCADE, null=True, blank=True)

    date_registered     = models.DateField(default=now, null=True, blank=True)
    last_updated        = models.DateTimeField(auto_now=True, editable=True)

    area                = models.ForeignKey('Area', related_name="area", on_delete=models.CASCADE, null=True, blank=True)
    farm_address        = models.CharField(max_length=200)
    loc_long            = models.FloatField(null=True, blank=True)
    loc_lat             = models.FloatField(null=True, blank=True)

    directly_manage     = models.BooleanField(default=False)
    wh_length           = models.FloatField(null=True, blank=True)
    wh_width            = models.FloatField(null=True, blank=True)
    roof_height         = models.FloatField(null=True, blank=True)
    num_pens            = models.IntegerField(null=True, blank=True, default=1)
    total_pigs          = models.IntegerField(null=True, blank=True)
    
    FEED_CHOICES        = [('Semi-automatic', 'Semi-automatic'),
                            ('Trough', 'Trough')]

    feed_trough         = models.CharField(max_length=15, choices=FEED_CHOICES, default='Semi-automatic')
    bldg_cap            = models.IntegerField(null=True, blank=True)
    
    bldg_curtain        = models.BooleanField(default=False)

    MED_TANK_CHOICES    = [('25 GAL', '25 GAL'),
                            ('50 GAL', '50 GAL')]

    medic_tank          = models.CharField(max_length=10, choices=MED_TANK_CHOICES, default='25 GAL')
    road_access         = models.BooleanField(default=False)
    
    extbio              = models.ForeignKey('ExternalBiosec', on_delete=models.SET_NULL, null=True, blank=True)
    intbio              = models.ForeignKey('InternalBiosec', on_delete=models.SET_NULL, null=True, blank=True)

    farm_weight         = models.ForeignKey('Farm_Weight', on_delete=models.CASCADE, null=True, blank=True)
    hog_symptoms       = models.ForeignKey('Hog_Symptoms', on_delete=models.CASCADE, null=True, blank=True)

    is_approved         = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.raiser_ID

# PIGPEN MEASURES Table
class Pigpen_Measures(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.CASCADE, related_name='+', null=True, blank=True)

    length              = models.FloatField()
    width               = models.FloatField()
    num_heads           = models.IntegerField()

    # def __str__(self)
    #     return self.

# ACTIVITY Table
class Activity(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.CASCADE, related_name='+', null=True, blank=True)

    date                = models.DateField()

    TYPE_CHOICES        = [('Delivery of Feeds', 'Delivery of Feeds'),
                            ('Delivery of Medicine', 'Delivery of Medicine'),
                            ('Delivery of Pigs', 'Delivery of Pigs'),
                            ('Vaccinations', 'Vaccinations'),
                            ('Inspection', 'Inspection'),
                            ('Trucking', 'Trucking'),
                            ('Other', 'Other')]

    trip_type           = models.CharField(max_length=50, choices=TYPE_CHOICES)
    time_departure      = models.TimeField()
    time_arrival        = models.TimeField()
    description         = models.CharField(max_length=500, null=True, blank=True)
    remarks             = models.CharField(max_length=500, null=True, blank=True)

    last_updated        = models.DateTimeField(auto_now=True, editable=True)
    is_approved         = models.BooleanField(default=False)

    # def __str__(self)
    #     return self.

# MORTALITY Table
class Mortality(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.CASCADE, related_name='+', null=True, blank=True)
        
    area                = models.CharField(max_length=15)
    series              = models.IntegerField()

    mortality_date      = models.DateTimeField()
    num_begInv          = models.IntegerField()
    num_today           = models.IntegerField()
    num_toDate          = models.IntegerField()
    source              = models.CharField(max_length=200)
    remarks             = models.CharField(max_length=500)
    
    # def __str__(self)
    #     return self.

# ACTIVITIES FORM Table
class Activities_Form(models.Model):
    ref_activity        = models.ForeignKey('Activity', on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    
    act_tech            = models.ForeignKey('User', on_delete=models.CASCADE, related_name='act_tech', null=True, blank=True)
    act_liveop          = models.ForeignKey('User', on_delete=models.CASCADE, related_name='act_liveop', null=True, blank=True)
    is_checked          = models.BooleanField(default=False)
    act_extvet          = models.ForeignKey('User', on_delete=models.CASCADE, related_name='act_extvet',  null=True, blank=True)
    is_reported         = models.BooleanField(default=False)
    act_asm             = models.ForeignKey('User', on_delete=models.CASCADE, related_name='act_asm',  null=True, blank=True)
    is_noted            = models.BooleanField(default=False)

# PPE FORM (Pigpen Evaluation) Table
class PPE_Form(models.Model):
    ref_farm            = models.ForeignKey('Farm', on_delete=models.CASCADE, related_name='+', null=True, blank=True)

    ppe_tech            = models.ForeignKey('User', on_delete=models.CASCADE, related_name='ppe_tech', null=True, blank=True)
    ppe_extvet          = models.ForeignKey('User', on_delete=models.CASCADE, related_name='ppe_extvet', null=True, blank=True)
    is_checked          = models.BooleanField(default=False)
    ppe_asm             = models.ForeignKey('User', on_delete=models.CASCADE, related_name='ppe_asm', null=True, blank=True)
    is_approved         = models.BooleanField(default=False)

# MORTALITY FORM Table
class Mortality_Form(models.Model):
    ref_mortality       = models.ForeignKey('Mortality', on_delete=models.CASCADE, related_name='+', null=True, blank=True)

    mort_tech           = models.ForeignKey('User', on_delete=models.CASCADE, related_name='mortTech',  null=True, blank=True)
    mort_mgtStaff       = models.ForeignKey('User', on_delete=models.CASCADE, related_name='mort_mgtStaff', null=True, blank=True)
    is_posted           = models.BooleanField(default=False)
    mort_extvet         = models.ForeignKey('User', on_delete=models.CASCADE, related_name='mort_extvet', null=True, blank=True)
    is_reported         = models.BooleanField(default=False)
    mort_asm            = models.ForeignKey('User', on_delete=models.CASCADE, related_name='mort_asm', null=True, blank=True)
    is_noted            = models.BooleanField(default=False)

# MEMBER ANNOUNCEMENT Table
class Mem_Announcement(models.Model):
    title               = models.CharField(max_length=150)
    category            = models.CharField(max_length=50)
    recip_area          = models.CharField(max_length=20)
    mssg                = models.CharField(max_length=500)
    author              = models.ForeignKey('User', on_delete=models.CASCADE, related_name='author', null=True, blank=True)
    timestamp           = models.DateTimeField(default=now)
    is_approved         = models.BooleanField(default=False)

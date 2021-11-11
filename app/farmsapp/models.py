from typing_extensions import ParamSpec
from django.db import models
# for getting current Date and Time when table record is created
from django.utils.timezone import now 


# Create your models here.
# USER Table
# EXTERNAL_BIOSEC Table
class ExternalBiosec(models.Model):
    last_updated = models.DateTimeField(default=now, editable=False)

    bird_proof          = models.IntegerField(null=True)
    perim_fence         = models.IntegerField(null=True)
    fiveh_m_dist        = models.IntegerField(null=True)

    prvdd_foot_dip      = models.IntegerField(null=True)
    prvdd_alco_soap     = models.IntegerField(null=True)
    obs_no_visitors     = models.IntegerField(null=True)
    prsnl_dip_footwear  = models.IntegerField(null=True)
    prsnl_sanit_hands   = models.IntegerField(null=True)
    chg_disinfect_daily = models.IntegerField(null=True)

    # def __str__(self):
    #     return self.id

# INTERNAL_BIOSEC Table
class InternalBiosec(models.Model):
    last_updated        = models.DateTimeField(default=now, editable=False)

    isol_pen            = models.IntegerField(null=True)
    waste_mgt           = models.IntegerField(null=True)
    foot_dip            = models.IntegerField(null=True)
    
    disinfect_prem      = models.IntegerField(null=True)
    disinfect_vet_supp  = models.IntegerField(null=True)

    # def __str__(self):
    #     return self.id

# FARM_WEIGHT Table
class Farm_Weight(models.Model):
    date_filed          = models.DateField()

    is_starter          = models.BooleanField(default=False)
    ave_weight          = models.FloatField()
    total_numHeads      = models.IntegerField()
    total_kls           = models.FloatField()

    # def __str__(self):
    #     return self.id

# FARM_SYMPTOMS Table
class Farm_Symptoms(models.Model):
    date_filed          = models.DateField()

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
    waste_mgt           = models.BooleanField(default=False)
    boar_dec_libido     = models.BooleanField(default=False)
    farrow_miscarriage  = models.BooleanField(default=False)
    weight_loss         = models.BooleanField(default=False)
    trembling           = models.BooleanField(default=False)
    conjunctivitis      = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.id

# HOG_RAISER Table
class Hog_Raiser(models.Model):
    fname               = models.CharField(max_length=50)
    lname               = models.CharField(max_length=50)
    contact_no          = models.CharField(max_length=15)

    # def __str__(self)
    #     return self.
# FARM Table
class Farm(models.Model): #28
    id                  = models.BigAutoField(primary_key=True)
    date_registered     = models.DateField()
    farm_address        = models.CharField(max_length=200)
    area                = models.CharField(max_length=15)
    loc_long            = models.FloatField()
    loc_lat             = models.FloatField()
    bldg_cap            = models.IntegerField()
    num_pens            = models.IntegerField()
    directly_manage     = models.BooleanField(default=False)
    total_pigs          = models.IntegerField()
    isolation_pen       = models.BooleanField(default=False)
    roof_height         = models.FloatField()
    feed_trough         = models.BooleanField(default=False)
    bldg_curtain        = models.BooleanField(default=False)
    medic_tank          = models.IntegerField()
    waste_mgt_septic    = models.BooleanField(default=False)
    waste_mgt_biogas    = models.BooleanField(default=False)
    waste_mgt_others    = models.BooleanField(default=False)
    warehouse_length    = models.FloatField()
    warehouse_width     = models.FloatField()
    road_access         = models.BooleanField(default=False)
    extbio_ID           = models.ForeignKey(ExternalBiosec, on_delete=models.CASCADE, null=True)
    intbio_ID           = models.ForeignKey(InternalBiosec, on_delete=models.CASCADE, null=True)
    raiser_ID           = models.ForeignKey(Hog_Raiser, on_delete=models.CASCADE, null=True)
    weight_record_ID    = models.ForeignKey(Farm_Weight, on_delete=models.CASCADE, null=True)
    symptoms_record_ID  = models.ForeignKey(Farm_Symptoms, on_delete=models.CASCADE, null=True)


# PIGPEN_MEASURES Table
class Pigpen_Measures(models.Model):
    farm_ID = models.ForeignKey(Farm, on_delete=models.CASCADE)

    length              = models.FloatField()
    width               = models.FloatField()
    num_heads           = models.IntegerField()

    # def __str__(self)
    #     return self.

# DELIVERY Table
class Delivery(models.Model):
    date_filed          = models.IntegerField()
   
    seller_fname        = models.CharField(max_length=50)
    seller_lname        = models.CharField(max_length=50)
    delivery_type       = models.CharField(max_length=30)
    qty                 = models.IntegerField()

    # def __str__(self)
    #     return self.

# ACTIVITY Table
class Activity(models.Model):
    farm_ID             = models.ForeignKey(Farm, on_delete=models.CASCADE)
    delivery_ID         = models.ForeignKey(Delivery, on_delete=models.CASCADE)

    date                = models.DateField()
    trip_desc           = models.CharField(max_length=500)
    time_departure      = models.DateTimeField()
    time_arrival        = models.DateTimeField()
    description         = models.CharField(max_length=500)
    remarks             = models.CharField(max_length=500)

    # def __str__(self)
    #     return self.

# MORTALITY Table
class Mortality(models.Model):
    farm_ID             = models.ForeignKey(Farm, on_delete=models.CASCADE)
        
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

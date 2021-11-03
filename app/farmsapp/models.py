from django.db import models
# for getting current Date and Time when table record is created
from django.utils.timezone import now 

# FARM Table
class Farm(models.Model): 
    # farm_code = models.IntegerField()

    date_registered = models.DateField()
    farm_address = models.CharField(max_length=200)
    area = models.CharField(max_length=15)
    loc_long = models.FloatField()
    loc_lat = models.FloatField()
    
    bldg_cap = models.IntegerField()
    num_pens = models.IntegerField()
    directly_manage = models.BooleanField(default=False)
    total_pigs = models.IntegerField()
    isolation_pen = models.BooleanField(default=False)
    roof_height = models.FloatField()
    feed_trough = models.BooleanField(default=False)
    bldg_curtain = models.BooleanField(default=False)
    medic_tank = models.IntegerField()
    waste_mgt_septic = models.BooleanField(default=False)
    waste_mgt_biogas = models.BooleanField(default=False)
    waste_mgt_others = models.BooleanField(default=False)
    warehouse_length = models.FloatField()
    warehouse_width = models.FloatField()
    road_access = models.BooleanField(default=False)
    
    extbio_ID = models.IntegerField()
    intbio_ID = models.IntegerField()

    est_time_complete = models.DateField()

    weight_record_ID = models.IntegerField()
    symptoms_record_ID = models.IntegerField()

    # def __str__(self)
    #     return self.farmer_code

# HOG_RAISER Table
class Hog_Raiser(models.Model):
    farm_ID = models.ForeignKey(Farm, on_delete=models.CASCADE)

    code = models.IntegerField()
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    contact_no = models.CharField(max_length=15)
    address = models.CharField(max_length=100)

    # def __str__(self)
    #     return self.

# PIGPEN_MEASURES Table
class Pigpen_Measures(models.Model):
    farm_ID = models.ForeignKey(Farm, on_delete=models.CASCADE)

    length = models.FloatField()
    width = models.FloatField()
    num_heads = models.IntegerField()

    # def __str__(self)
    #     return self.

# DELIVERY Table
class Delivery(models.Model):
    date_filed = models.IntegerField()
    seller_fname = models.CharField(max_length=50)
    seller_lname = models.CharField(max_length=50)
    delivery_type = models.CharField(max_length=30)
    qty = models.IntegerField()

# ACTIVITY Table
class Activity(models.Model):
    farm_ID = models.ForeignKey(Farm, on_delete=models.CASCADE)
    delivery_ID = models.ForeignKey(Delivery, on_delete=models.CASCADE)

    date = models.DateField()
    trip_desc = models.CharField(max_length=500)
    time_departure = models.DateTimeField()
    time_arrival = models.DateTimeField()
    description = models.CharField(max_length=500)
    remarks = models.CharField(max_length=500)

    # def __str__(self)
    #     return self.
# Create your models here.

# TODO: internal, external biosec models
class ExternalBiosec(models.Model):
    # TODO: generate custom PK?
    # id = models.CharField(max_length=100)
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

class InternalBiosec(models.Model):
    # TODO: generate custom PK?
    # id = models.CharField(max_length=100)
    last_updated = models.DateTimeField(default=now, editable=False)

    isol_pen            = models.IntegerField(null=True)
    waste_mgt           = models.IntegerField(null=True)
    foot_dip            = models.IntegerField(null=True)
    
    disinfect_prem      = models.IntegerField(null=True)
    disinfect_vet_supp  = models.IntegerField(null=True)

    # def __str__(self):
    #     return self.id
            

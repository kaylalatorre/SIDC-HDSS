from django.db import models

# FARM Table
class Farm(models.Model):
    date_registered = models.DateField()
    date_filed = models.DateField()
    raiser_uname = models.CharField(max_length=50)
    raiser_lname = models.CharField(max_length=50)
    farmer_contact = models.CharField(max_length=50)
    farmer_address = models.CharField(max_length=200)
    farmer_code = models.IntegerField()
    area = models.CharField(max_length=15)
    # loc_long = models.FloatField()
    # loc_lat = models.FloatField()
    
    user_id = models.IntegerField()
    num_headsApplied = models.IntegerField()
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
    
    internal_bio_ID = models.IntegerField()
    external_bio_ID = models.IntegerField()

    est_time_complete = models.DateField()
    activity_ID = models.IntegerField

    weight_record_ID = models.IntegerField()
    symptoms_record_ID = models.IntegerField()

# USER Table
from django.db import models

# FARM Table
# class Farm(models.Model):
#     date_registered = models.DateField()
#     date_filed = models.DateField()
#     raiser_uname = models.CharField(max_length=50)
#     raiser_lname = models.CharField(max_length=50)
#     farmer_contact = models.CharField(max_length=50)
#     farmer_address = models.CharField(max_length=200)
#     farmer_code = models.IntegerField()
#     area = models.CharField(max_length=15)
#     # loc_long = models.FloatField()
#     # loc_lat = models.FloatField()
    
#     user_id = models.IntegerField()
#     # user_id = models.ForeignKey(User, )
#     num_headsApplied = models.IntegerField()
#     bldg_cap = models.IntegerField()
#     num_pens = models.IntegerField()
#     directly_manage = models.BooleanField(default=False)
#     total_pigs = models.IntegerField()
#     isolation_pen = models.BooleanField(default=False)
#     roof_height = models.FloatField()
#     feed_trough = models.BooleanField(default=False)
#     bldg_curtain = models.BooleanField(default=False)
#     medic_tank = models.IntegerField()
#     waste_mgt_septic = models.BooleanField(default=False)
#     waste_mgt_biogas = models.BooleanField(default=False)
#     waste_mgt_others = models.BooleanField(default=False)
#     warehouse_length = models.FloatField()
#     warehouse_width = models.FloatField()
#     road_access = models.BooleanField(default=False)
    
#     internal_bio_ID = models.IntegerField()
#     external_bio_ID = models.IntegerField()

#     est_time_complete = models.DateField()
#     activity_ID = models.IntegerField

#     weight_record_ID = models.IntegerField()
#     symptoms_record_ID = models.IntegerField()

#     # def __str__(self)
#     #     return self.farmer_code

class Farm(models.Model): 
    date_registered = models.DateField(blank=True,null=True)
    date_filed = models.DateField(blank=True,null=True)
    raiser_uname = models.CharField(max_length=50,blank=True,null=True)
    raiser_lname = models.CharField(max_length=50,blank=True,null=True)
    farmer_contact = models.CharField(max_length=50,blank=True,null=True)
    farmer_address = models.CharField(max_length=200,blank=True,null=True)
    farmer_code = models.IntegerField(blank=True,null=True)
    area = models.CharField(max_length=15,blank=True,null=True)
    # loc_long = models.FloatField()
    # loc_lat = models.FloatField()
    
    user_id = models.IntegerField(blank=True,null=True)
    # user_id = models.ForeignKey(User, )
    num_headsApplied = models.IntegerField(blank=True,null=True)
    bldg_cap = models.IntegerField(blank=True,null=True)
    num_pens = models.IntegerField(blank=True,null=True)
    directly_manage = models.BooleanField(default=False,blank=True,null=True)
    total_pigs = models.IntegerField(blank=True,null=True)
    isolation_pen = models.BooleanField(default=False,blank=True,null=True)
    roof_height = models.FloatField(blank=True,null=True)
    feed_trough = models.BooleanField(default=False,blank=True,null=True)
    bldg_curtain = models.BooleanField(default=False,blank=True,null=True)
    medic_tank = models.IntegerField(blank=True,null=True)
    waste_mgt_septic = models.BooleanField(default=False,blank=True,null=True)
    waste_mgt_biogas = models.BooleanField(default=False,blank=True,null=True)
    waste_mgt_others = models.BooleanField(default=False,blank=True,null=True)
    warehouse_length = models.FloatField(blank=True,null=True)
    warehouse_width = models.FloatField(blank=True,null=True)
    road_access = models.BooleanField(default=False,blank=True,null=True)
    
    internal_bio_ID = models.IntegerField(blank=True,null=True)
    external_bio_ID = models.IntegerField(blank=True,null=True)

    est_time_complete = models.DateField(blank=True,null=True)
    activity_ID = models.IntegerField(blank=True,null=True)

    weight_record_ID = models.IntegerField(blank=True,null=True)
    symptoms_record_ID = models.IntegerField(blank=True,null=True)

    # def __str__(self)
    #     return self.farmer_code

# ACTIVITY Table
class Activity(models.Model):
    date = models.DateField()
    raiser_ID = models.IntegerField()
    trip_description = models.CharField(max_length=500)
    time_departure = models.DateTimeField()
    time_arrival = models.DateTimeField()
    description = models.CharField(max_length=500)
    remarks = models.CharField(max_length=500)
    technician_ID = models.IntegerField()

    # def __str__(self)
    #     return self.
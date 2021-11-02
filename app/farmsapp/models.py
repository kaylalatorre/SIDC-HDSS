from typing_extensions import ParamSpec
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
    feed_through = models.BooleanField(default=False)
    bldg_curtain = models.BooleanField(default=False)
    medic_tank = models.IntegerField()
    waste_mgt_septic = models.BooleanField(default=False)
    waste_mgt_biogas = models.BooleanField(default=False)
    waste_mgt_others = models.BooleanField(default=False)
    warehouse_length = models.FloatField()
    warehouse_width = models.FloatField()
    road_access = models.BooleanField(default=False)
    
    internal_bio_ID = models.IntegerField(null=True)
    external_bio_ID = models.IntegerField(null=True)

    est_time_complete = models.DateField()
    activity_ID = models.IntegerField()

    weight_record_ID = models.IntegerField()
    symptoms_record_ID = models.IntegerField()

    def __str__(self) -> str:
        return '%s %s' % (self.raiser_uname, self.raiser_lname)
   
    @classmethod
    def create(cls, date_registered, date_filed, raiser_uname, raiser_lname,
        farmer_contact, farmer_address, farmer_code, area,
        # loc_long, # loc_lat,
        user_id, num_headsApplied, bldg_cap, num_pens,
        directly_manage, total_pigs, isolation_pen, roof_height,
        feed_through, bldg_curtain, medic_tank, waste_mgt_septic,
        waste_mgt_biogas, waste_mgt_others, warehouse_length, warehouse_width,
        road_access, internal_bio_ID, external_bio_ID, est_time_complete,
        activity_ID, weight_record_ID, symptoms_record_ID,):
        """
        Create an instance of Farm

        :param date_registered:     models.DateField()
        :param date_filed:          models.DateField()
        :param raiser_uname:        models.CharField(max_length=50)
        :param raiser_lname:        models.CharField(max_length=50)
        :param farmer_contact:      models.CharField(max_length=50)
        :param farmer_address:      models.CharField(max_length=200)
        :param farmer_code:         models.IntegerField()
        :param area:                models.CharField(max_length=15)
        :param loc_long:            models.FloatField()
        :param loc_lat:             models.FloatField()
        :param user_id:             models.IntegerField()
        :param num_headsApplied:    models.IntegerField()
        :param bldg_cap:            models.IntegerField()
        :param num_pens:            models.IntegerField()
        :param directly_manage:     models.BooleanField(default=False)
        :param total_pigs:          models.IntegerField()
        :param isolation_pen:       models.BooleanField(default=False)
        :param roof_height:         models.FloatField()
        :param feed_through:        models.BooleanField(default=False)
        :param bldg_curtain:        models.BooleanField(default=False)
        :param medic_tank:          models.IntegerField()
        :param waste_mgt_septic:    models.BooleanField(default=False)
        :param waste_mgt_biogas:    models.BooleanField(default=False)
        :param waste_mgt_others:    models.BooleanField(default=False)
        :param warehouse_length:    models.FloatField()
        :param warehouse_width:     models.FloatField()
        :param road_access:         models.BooleanField(default=False)
        :param internal_bio_ID:     models.IntegerField(null=True)
        :param external_bio_ID:     models.IntegerField(null=True)
        :param est_time_complete:   models.DateField()
        :param activity_ID:         models.IntegerField()
        :param weight_record_ID:    models.IntegerField()
        :param symptoms_record_ID:  models.IntegerField()
        """
        farm = cls(date_registered = date_registered, date_filed = date_filed, raiser_uname = raiser_uname,
            raiser_lname = raiser_lname, farmer_contact = farmer_contact, farmer_address = farmer_address,
            farmer_code = farmer_code, area = area,
            # loc_long = loc_long, # loc_lat = loc_lat,
            user_id = user_id, num_headsApplied = num_headsApplied, bldg_cap = bldg_cap,
            num_pens = num_pens, directly_manage = directly_manage, total_pigs = total_pigs,
            isolation_pen = isolation_pen, roof_height = roof_height, feed_through = feed_through,
            bldg_curtain = bldg_curtain, medic_tank = medic_tank, waste_mgt_septic = waste_mgt_septic,
            waste_mgt_biogas = waste_mgt_biogas, waste_mgt_others = waste_mgt_others, warehouse_length = warehouse_length,
            warehouse_width = warehouse_width, road_access = road_access, internal_bio_ID = internal_bio_ID,
            external_bio_ID = external_bio_ID, est_time_complete = est_time_complete, activity_ID = activity_ID,
            weight_record_ID = weight_record_ID, symptoms_record_ID = symptoms_record_ID,)
        return farm

# USER Table
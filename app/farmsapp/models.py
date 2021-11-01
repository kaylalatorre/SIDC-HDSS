from django.db import models

# Create your models here.

# TODO: internal, external biosec models
class ExternalBiosec(models.Model):
    # TODO: generate custom PK?
    # id = models.CharField(max_length=100)
    # last_updated = models.DateTimeField('last_updated')

    bird_proof          = models.IntegerField()
    perim_fence         = models.IntegerField()
    fiveh_m_dist        = models.IntegerField()

    prvdd_foot_dip      = models.IntegerField()
    prvdd_alco_soap     = models.IntegerField()
    obs_no_visitors     = models.IntegerField()
    prsnl_dip_footwear  = models.IntegerField()
    prsnl_sanit_hands   = models.IntegerField()
    chg_disinfect_daily = models.IntegerField()

    # def __str__(self):
    #     return self.id

class InternalBiosec(models.Model):
    # TODO: generate custom PK?
    # id = models.CharField(max_length=100)
    # last_updated = models.DateTimeField('last_updated')

    isol_pen            = models.IntegerField()
    waste_mgt           = models.IntegerField()
    foot_dip            = models.IntegerField()
    
    disinfect_prem      = models.IntegerField()
    disinfect_vet_supp  = models.IntegerField()

    # def __str__(self):
    #     return self.id
            
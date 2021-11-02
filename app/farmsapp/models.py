from django.db import models
# for getting current Date and Time when table record is created
from django.utils.timezone import now 

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
            
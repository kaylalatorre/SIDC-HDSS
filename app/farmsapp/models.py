from django.db import models
# for getting current Date and Time when table record is created
from django.utils.timezone import now 

# Create your models here.

class Farm(models.Model): 
    extbio              = models.ForeignKey('ExternalBiosec', on_delete=models.CASCADE, null=True, blank=True)
    intbio              = models.ForeignKey('InternalBiosec', on_delete=models.CASCADE, null=True, blank=True)

class ExternalBiosec(models.Model):
    ref_farm = models.ForeignKey('Farm', on_delete=models.CASCADE, related_name='+', null=True, blank=True)

    last_updated = models.DateTimeField(default=now, editable=False)
    # fields from Biomeasures
    bird_proof          = models.IntegerField(null=True)
    perim_fence         = models.IntegerField(null=True)
    fiveh_m_dist        = models.IntegerField(null=True)
    # fields from Biochecklist
    prvdd_foot_dip      = models.IntegerField(null=True)
    prvdd_alco_soap     = models.IntegerField(null=True)
    obs_no_visitors     = models.IntegerField(null=True)
    prsnl_dip_footwear  = models.IntegerField(null=True)
    prsnl_sanit_hands   = models.IntegerField(null=True)
    chg_disinfect_daily = models.IntegerField(null=True)

    # TODO: getter function to return specific fields (?)

    # def __str__(self):
    #     return self.id

class InternalBiosec(models.Model):
    ref_farm = models.ForeignKey('Farm', on_delete=models.CASCADE, related_name='+', null=True, blank=True)

    last_updated = models.DateTimeField(default=now, editable=False)
    # fields from Biomeasures
    isol_pen            = models.IntegerField(null=True)
    waste_mgt           = models.IntegerField(null=True)
    foot_dip            = models.IntegerField(null=True)
    # fields from Biochecklist
    disinfect_prem      = models.IntegerField(null=True)
    disinfect_vet_supp  = models.IntegerField(null=True)

    # TODO: getter function to return specific fields (?)

    # def __str__(self):
    #     return self.id
            
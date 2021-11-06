from django import forms

class FarmForm(forms.Form):
    # date_registered     = forms.DateField()

    farm_address        = forms.CharField(max_length=200)
    area                = forms.CharField(max_length=15)
    loc_long            = forms.FloatField()
    loc_lat             = forms.FloatField()
    
    bldg_cap            = forms.IntegerField()
    num_pens            = forms.IntegerField()
    directly_manage     = forms.BooleanField()
    total_pigs          = forms.IntegerField()
    isolation_pen       = forms.BooleanField()
    roof_height         = forms.FloatField()
    feed_trough         = forms.BooleanField()
    bldg_curtain        = forms.BooleanField()
    medic_tank          = forms.IntegerField()
    waste_mgt_septic    = forms.BooleanField()
    waste_mgt_biogas    = forms.BooleanField()
    waste_mgt_others    = forms.BooleanField()
    warehouse_length    = forms.FloatField()
    warehouse_width     = forms.FloatField()
    road_access         = forms.BooleanField()

    # extbio_ID           = forms.IntegerField()
    # intbio_ID           = forms.IntegerField()

    # est_time_complete   = forms.DateField()
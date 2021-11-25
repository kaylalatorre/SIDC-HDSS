from django import forms
from django.forms import ModelForm
from .models import Farm, Hog_Raiser, Pigpen_Measures, ExternalBiosec, InternalBiosec, Farm_Weight, Farm_Symptoms, Delivery, Activity, Mortality, Mem_Announcement

class DateInput(ModelForm):
    input_type = 'date'

class ExternalBiosecForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bird_proof'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-isolation'         
        })
        self.fields['perim_fence'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-fence'         
        })
        self.fields['fiveh_m_dist'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-distance'         
        })

    class Meta:
        model = ExternalBiosec
        fields = ('__all__')

class InternalBiosecForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['isol_pen'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-isolation'         
        })
        self.fields['foot_dip'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-footdip'         
        })

    class Meta:
        model = InternalBiosec
        fields = ('__all__')

class FarmWeightForm(ModelForm):
    class Meta:
        model = Farm_Weight
        fields = ('__all__')

class FarmSymptomsForm(ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields[''].widget.attrs.update({
   
    class Meta:
        model = Farm_Symptoms
        fields = ('__all__')

class FarmForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['directly_manage'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-directly', 
            'name' : 'cb-directly'            
        })
        self.fields['farm_address'].widget.attrs.update({
            'input type' : 'text', 
            'class' : 'form-control',
            'id' : 'input-address',
            'name' : 'input-address',
            'placeholder' : 'ex. Batangas, 4200 Batangas'
        })
        self.fields['area'].widget.attrs.update({
           'select class' : 'form-select',
           'id' : 'input-area'
        })
        self.fields['roof_height'].widget.attrs.update({
            'input type' : 'number', 
            'class' : 'form-control',
            'id' : 'input-roof',
            'name' : 'input-roof',
            'placeholder' : 'ex. 100'
        })
        self.fields['warehouse_length'].widget.attrs.update({
            'input type' : 'number',
            'aria-label' : 'Length', 
            'class' : 'form-control',
            'id' : 'wh-length',
            'name' : 'wh-length',
            'placeholder' : 'Length'
        })
        self.fields['warehouse_width'].widget.attrs.update({
            'input type' : 'number',
            'aria-label' : 'Width', 
            'class' : 'form-control',
            'id' : 'wh-width',
            'name' : 'wh-width',
            'placeholder' : 'Width'
        })
        self.fields['feed_trough'].widget.attrs.update({
           'select class' : 'form-select',
           'id' : 'input-trough'
        })
        self.fields['bldg_cap'].widget.attrs.update({
            'input type' : 'number', 
            'class' : 'form-control',
            'id' : 'input-roof',
            'name' : 'input-roof',
            'placeholder' : 'ex. 100'
        })

    class Meta:
        model = Farm
        fields = ('__all__')

class HogRaiserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fname'].widget.attrs.update({
            'input type' : 'text', 
            'class' : 'form-control',
            'id' : 'input-first-name',
            'name' : 'input-first-name',
            'placeholder' : 'ex. John'
        })
        self.fields['lname'].widget.attrs.update({
            'input type' : 'text', 
            'class' : 'form-control',
            'id' : 'input-last-name',
            'name' : 'input-last-name',
            'placeholder' : 'ex. Doe'
        })
        self.fields['contact_no'].widget.attrs.update({
            'input type' : 'text', 
            'class' : 'form-control',
            'id' : 'input-contact',
            'name' : 'input-contact',
            'placeholder' : 'ex. 091512345678'
        })
            
    class Meta:
        model = Hog_Raiser
        fields = ('__all__')

class PigpenMeasuresForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['length'].widget.attrs.update({
            'input type' : 'number', 
            'aria-label' : 'Length',
            'class' : 'form-control',
            'placeholder' : 'Length'
        })
        self.fields['width'].widget.attrs.update({
            'input type' : 'number', 
            'aria-label' : 'Width',
            'class' : 'form-control',
            'placeholder' : 'Width'
        })
        self.fields['num_heads'].widget.attrs.update({
            'input type' : 'number', 
            'aria-label' : 'No. of Pigs',
            'class' : 'form-control',
            'placeholder' : 'ex. 100'
        })

    class Meta:
        model = Pigpen_Measures
        fields = ('__all__')

class DeliveryForm(ModelForm):
    class Meta:
        model = Delivery
        fields = ('__all__')

class ActivityForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({
            'type' : 'date', 
            'aria-label' : 'Date',
            'class' : 'form-control',
            'placeholder' : '01/01/2021'
        })
        self.fields['time_departure'].widget.attrs.update({
            'type' : 'time', 
            'aria-label' : 'Departure Time',
            'class' : 'form-control',
            'placeholder' : '18:00'
        })
        self.fields['time_arrival'].widget.attrs.update({
            'input type' : 'time', 
            'aria-label' : 'Arrival Time',
            'class' : 'form-control',
            'placeholder' : '18:00'
        })
        self.fields['description'].widget.attrs.update({
            'input type' : 'text', 
            'aria-label' : 'Description',
            'class' : 'form-control',
            'placeholder' : 'Description'
        })
        self.fields['remarks'].widget.attrs.update({
            'input type' : 'text', 
            'aria-label' : 'Remarks',
            'class' : 'form-control',
            'placeholder' : 'Remarks'
        })

    class Meta:
        model = Activity
        fields = ('__all__')

class MortalityForm(ModelForm):
    class Meta:
        model = Mortality
        fields = ('__all__')

class MemAnnouncementForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'input type' : 'text', 
            'aria-label' : 'Title',
            'class' : 'form-control',
            'placeholder' : 'ex. Biosecurity Check'
        })
        self.fields['category'].widget.attrs.update({ 
            'aria-label' : 'Category',
            'class' : 'form-select'
        })
        self.fields['recip_area'].widget.attrs.update({ 
            'aria-label' : 'Recipient',
            'class' : 'form-select',
        })
        self.fields['mssg'].widget.attrs.update({ 
            'aria-label' : 'Message',
            'class' : 'form-control',
            'placeholder' : 'Construct your message here'
        })

    class Meta:
        model = Mem_Announcement
        fields = ('__all__')
        widgets = {
            'category': forms.Select(
                choices=(('Reminder','Reminder'), ('Announcement','Announcement'), ('Event','Event'), ('Other','Other'))
            ),
            'recip_area': forms.Select(
                choices=(('All Raisers','All Raisers'), ('TISISI Raisers','TISISI Raisers'), ('West Raisers','West Raisers'), ('East Raisers','East Raisers'))
            ),
            'mssg': forms.Textarea()
        }
from django import forms
from django.forms import ModelForm, DateField, widgets
from .models import Farm, Hog_Raiser, Pigpen_Measures, ExternalBiosec, InternalBiosec, Farm_Weight, Hog_Symptoms, Activity, Mortality, Area
import datetime

class DateInput(ModelForm):
    input_type = 'date'

class ExternalBiosecForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bird_proof'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-birdproof',
            # 'value' : '1'               
        })
        self.fields['perim_fence'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-fence',
            # 'value' : '1'               
        })
        self.fields['fiveh_m_dist'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-distance',
            # 'value' : '1'         
        })
    
    def clean_active(self):
        return 0 if self.cleaned_data['active'] else 1

    class Meta:
        model = ExternalBiosec
        fields = ('__all__')
        # widgets = {
        #     'bird_proof' : widgets.CheckboxInput(),
        #     'perim_fence' : widgets.CheckboxInput(),
        #     'fiveh_m_dist' : widgets.CheckboxInput(),
        # }

# class ExternalBiosecForm(forms.Form):
#     bird_proof = forms.CheckboxInput()
#     perim_fence = forms.CheckboxInput()
#     fiveh_m_dist = forms.CheckboxInput()

class InternalBiosecForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['isol_pen'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-isolation',
            # 'value' : '1'               
        })
        self.fields['foot_dip'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-footdip',
            # 'value' : '1'         
        })
        self.fields['waste_mgt'].widget.attrs.update({
           'select class' : 'form-select',
           'id' : 'input-waste-mgt'
        })

    class Meta:
        model = InternalBiosec
        fields = ('__all__')
        # widgets = {
        #     'isol_pen' : widgets.CheckboxInput(),
        #     'foot_dip' : widgets.CheckboxInput(),
        # }

class FarmWeightForm(ModelForm):
    class Meta:
        model = Farm_Weight
        fields = ('__all__')

class HogSymptomsForm(ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields[''].widget.attrs.update({
   
    class Meta:
        model = Hog_Symptoms
        fields = ('__all__')

class AreaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area_name'].widget.attrs.update({
           'select class' : 'form-select',
           'id' : 'input-area'
        })

    class Meta:
        model = Area
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
        self.fields['roof_height'].widget.attrs.update({
            'input type' : 'number', 
            'class' : 'form-control',
            'id' : 'input-roof',
            'name' : 'input-roof',
            'placeholder' : 'ex. 100'
        })
        self.fields['wh_length'].widget.attrs.update({
            'input type' : 'number',
            'aria-label' : 'Length', 
            'class' : 'form-control',
            'id' : 'wh-length',
            'name' : 'wh-length',
            'placeholder' : 'Length'
        })
        self.fields['wh_width'].widget.attrs.update({
            'input type' : 'number',
            'aria-label' : 'Width', 
            'class' : 'form-control',
            'id' : 'wh-width',
            'name' : 'wh-width',
            'placeholder' : 'Width'
        })
        self.fields['feed_trough'].widget.attrs.update({
           'select class' : 'form-select',
           'id' : 'input-trough',
        })
        self.fields['bldg_cap'].widget.attrs.update({
            'input type' : 'number', 
            'class' : 'form-control',
            'id' : 'input-roof',
            'name' : 'input-roof',
            'placeholder' : 'ex. 100'
        })
        self.fields['bldg_curtain'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-curtain', 
            'name' : 'cb-curtain'            
        })
        self.fields['road_access'].widget.attrs.update({
            'input type' : 'checkbox',
            'class' : 'form-check-input',
            'id': 'cb-road', 
            'name' : 'cb-road'            
        })
        self.fields['medic_tank'].widget.attrs.update({
           'select class' : 'form-select',
           'id' : 'inout-medic-tank',
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

class ActivityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({
            'type' : 'date', 
            'aria-label' : 'Date',
            'class' : 'form-control',
        })
        self.fields['trip_type'].widget.attrs.update({
           'select class' : 'form-select',
           'id' : 'act-trip-type',
           'style' : 'margin-bottom: 0',
        })
        self.fields['time_arrival'].widget.attrs.update({
            'input type' : 'time', 
            'aria-label' : 'Arrival Time',
            'class' : 'form-control',
        })
        self.fields['time_departure'].widget.attrs.update({
            'type' : 'time', 
            'aria-label' : 'Departure Time',
            'class' : 'form-control',
            'required' : 'True',
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
        widgets = {
            'date' : widgets.DateInput(attrs={'type' : 'date'}),
            'time_departure' : widgets.TimeInput(attrs={'type' : 'time'}),
            'time_arrival' : widgets.TimeInput(attrs={'type' : 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        date = cleaned_data.get("date")
        today = datetime.date.today()

        # print("Input Date: " + str(date))
        # print("Date today: " + str(today))

        if date > today:
            raise forms.ValidationError("Date can not be later than today.")

        time_arrival = cleaned_data.get("time_arrival")
        time_departure = cleaned_data.get("time_departure")

        # print("Arrival: " + str(time_arrival))
        # print("Departure: " + str(time_departure))

        if time_departure > time_arrival:
            raise forms.ValidationError("Arrival time should be after departure time.")

class MortalityForm(ModelForm):
    class Meta:
        model = Mortality
        fields = ('__all__')
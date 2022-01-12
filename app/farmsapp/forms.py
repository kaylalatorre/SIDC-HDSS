from django import forms
from django.forms import ModelForm, DateField, widgets, Select, Textarea
from .models import Farm, Hog_Raiser, Pigpen_Row, Farm_Weight, Hog_Symptoms, Activity, Mortality, Area, Mem_Announcement
import datetime

class DateInput(ModelForm):
    input_type = 'date'

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

class PigpenRowForm(ModelForm):
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
        model = Pigpen_Row
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

        if time_departure < time_arrival:
            raise forms.ValidationError("Arrival time should be before departure time.")

class MortalityForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mortality_date'].widget.attrs.update({
            'type' : 'date', 
            'class' : 'form-control',
            'id' : 'mortality-date', 
        })
        self.fields['num_today'].widget.attrs.update({
            'type' : 'number', 
            'class' : 'form-control',
            'id' : 'beg-inv', 
            'placeholder' : 'ex. 20',
        })                
        self.fields['source'].widget.attrs.update({
            'type' : 'text', 
            'class' : 'form-control',
            'id' : 'mortality-source', 
        })        
        self.fields['remarks'].widget.attrs.update({
            'type' : 'text', 
            'class' : 'form-control',
            'id' : 'mortality-remarks', 
        })

    class Meta:
        model = Mortality
        fields = ('__all__')
        widgets = {
            'mortality_date' : widgets.DateInput(attrs={'type' : 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()

        mortality_date = cleaned_data.get("mortality_date")
        today = datetime.date.today()

        # print("Input Date: " + str(mortality_date))
        # print("Date today: " + str(today))

        if mortality_date > today:
            raise forms.ValidationError("Date can not be later than today.")


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
        AREA_CHOICES = [('All Raisers', 'All Raisers')]

        for choice in Area.objects.distinct().values('area_name'):
            AREA_CHOICES.append((choice['area_name'], choice['area_name']))

        fields = ('__all__')
        widgets = {
            'category': widgets.Select(
                choices=(('Reminder','Reminder'), ('Announcement','Announcement'), ('Event','Event'), ('Other','Other'))
            ),
            'recip_area': widgets.Select(
                choices=AREA_CHOICES
            ),
            'mssg': widgets.Textarea()
        }

class WeightForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ave_weight'].widget.attrs.update({
            'aria-label' : 'Ave. Weight', 
            'type' : 'number',
            'class' : 'form-control',
            'placeholder': 'ex. 120',
            'min' : 0,
            'step' : 0.01
        })
        self.fields['total_numHeads'].widget.attrs.update({ 
            'aria-label' : 'Total No. of Heads', 
            'type' : 'number',
            'class' : 'form-control',
            'placeholder': 'ex. 100',
            'min' : 0
        })
        self.fields['total_kls'].widget.attrs.update({ 
            'aria-label' : 'kls', 
            'type' : 'number',
            'class' : 'form-control',
            'placeholder': 'ex. 120',
            'min' : 0,
            'step' : 0.01
        })
        self.fields['remarks'].widget.attrs.update({ 
            'aria-label' : 'Remarks', 
            'type' : 'text',
            'class' : 'form-control',
            'placeholder': ''
        })

    class Meta:
        model = Farm_Weight
        CHOICES = [('Starter', 'Starter'),
                    ('Fattener', 'Fattener')]
                    
        fields = ('__all__')
        widgets = {
           
            'is_starter': widgets.RadioSelect(choices=CHOICES)
        }
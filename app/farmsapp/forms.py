from django.forms import ModelForm
from .models import Farm

class FarmForm(ModelForm):
    class Meta:
        model = Farm
        fields = '__all__'
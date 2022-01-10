from django import template

register = template.Library()

# Custom functions that can be used within the app's templates.

# for Symptoms list; formats passed field name and replaces "_" with spaces.
@register.filter
def formatField(strField):

    if strField == "loss_appetite": # Note: can format other symptom fields using a similar if-condition
        return "loss of appetite"
    if strField == "death_isDays": 
        return "death within 6-13 days"
    if strField == "death_isWeek": 
        return "death (in less than 1 week old)"
    if strField == "vomit_diarrhea": 
        return "vomitting/diarrhea with bloody discharge"
    if strField == "colored_pigs": 
        return "white-skinned or cyanotice"
    if strField == "abn_breathing": 
        return "abnormal breathing"
    if strField == "discharge_eyesnose": 
        return "heavy discharge from eyes and/or nose"
    if strField == "cough": 
        return "coughing"
    if strField == "sneeze": 
        return "sneezing"
    if strField == "waste": 
        return "wasting"
    if strField == "boar_dec_libido ": 
        return "reduced libido (boars)"
    if strField == "farrow_miscarriage": 
        return "miscarriage (farrows)"
    if strField == "trembling": 
        return "trembling and incoordination"

    return strField.replace("_"," ")
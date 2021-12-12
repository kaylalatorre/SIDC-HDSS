from django import template

register = template.Library()

# Custom functions that can be used within the app's templates.

# for Symptoms list; formats passed field name and replaces "_" with spaces.
@register.filter
def formatField(strField):

    if strField == "loss_appetite": # Note: can format other symptom fields using a similar if-condition
        return "loss of appetite"

    return strField.replace("_"," ")
from django import template

register = template.Library()

# Custom functions that can be used within the app's templates.

# for Symptoms Monitoring, Tentative Diagnosis; 0 == Positive, 1 == Negative, 2 == Pending.
@register.filter
def labResult(strField):
    if strField == True: 
        return "Positive"
    if strField == False:
        return "Negative"
    # if strField == 2: 
    #     return "Pending"
    
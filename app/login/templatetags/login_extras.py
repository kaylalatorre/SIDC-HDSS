from django import template

register = template.Library()

# Custom functions that can be used within the app's templates.

# Concatenates two strings together separated by a ''.
@register.filter
def addStr(arg1, arg2):
    """concatenate arg1 & arg2"""
    # print("fname: " + arg1)
    # print("lname: " + arg2)
    return str(arg1) + " " + str(arg2)
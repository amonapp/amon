from __future__ import division
from django import template

register = template.Library()

@register.filter
def sum(element, second_element):
    result = float(element)+float(second_element)
    return result

@register.filter
def substract(element, second_element):
    result = float(element)-float(second_element)
    return result

@register.filter
def sum_int(element, second_element):
    result = element+second_element
    return result

@register.filter
def substract_int(element, second_element):
    result = 0
    if type(element) == int and type(second_element) == int:
        result = element-second_element
    return result

@register.filter
def percentage_of(element, second_element):
    percentage = '{0:.2f}'.format((element / second_element * 100))
    return percentage


# CSS Helper function, 20% to 0.2, 80% to 0.8
@register.filter
def percent_to_opacity(value):
    # Combining the calculations you can get the formula for P% * X = (P/100) * X = Y so 10% * 150 = (10/100) * 150 = 15
    value = float(value)
    result = (value / 100) * 1
    return     result
    

@register.filter
def divide(value, arg): return int(value) / int(arg)
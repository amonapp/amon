from django import template
register = template.Library()

    

@register.filter
def yaxis(value): 
    yaxis_value = ''
    if type(value) is str:
        value = value.lower()

    if value == 'cpu':
        yaxis_value = '%'
    elif value in ['memory', 'disk']:
        yaxis_value = 'MB'
    elif value in ['io','network']:
        yaxis_value = 'KB'

    if type(value) is dict:
        unit = value.get('unit', '')
        unit = '' if unit == None else unit
        yaxis_value = unit
    

    return yaxis_value


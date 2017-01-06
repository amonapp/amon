from __future__ import division
from django import template
from amon.utils.filesize import size

register = template.Library()

@register.filter
def kb_to_mb(value):
    mb = float(value)/1000
    mb = "{0:.2f}".format(mb)
    
    return mb


@register.filter
def seconds_to_minutes(value):
    minutes = value/60


    return minutes


# Used in alerts/all
@register.filter
def metric_type_value(value, metric):
    result = ""
    metric = metric.lower()

    if metric == 'memory':
        result = 'MB'
    elif metric == 'down':
        result = 'Down between'
    else:
        result = value 

    return result

@register.filter
def bytes_to_mb(value):

    return size(value)
    
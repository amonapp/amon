from django import template
from amon.utils.filesize import size
register = template.Library()


@register.filter
def format_plugin_value(value, column):
    if column in ['size', 'totalIndexSize', 'indexes', 'total', 'bytes']:
        try:
            value = size(value)
        except Exception as e:
            pass
            
    return value


@register.filter
def format_plugin_header(value):
    try:
        value = value.replace("_", " ").title()
    except:
        pass
            
    return value


@register.filter
def counter_to_int(value):
    if isinstance(value, float):
        value = int(value)

    return value
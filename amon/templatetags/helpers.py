import re
from django import template

register = template.Library()
from amon.utils.charts import get_disk_unit

@register.filter
def disk_unit(server):
    unit = get_disk_unit(server=server)

    return unit

@register.filter
def get_distro(distro):

    try:
        name = distro.get('name', '').lower()
    except:
        name = ''

    return name

@register.filter
def parse_ignored_list(list_with_values):
    result = []
    if list_with_values:
        for v in list_with_values:
            try:
                name, cpu, memory = v.split('::')
                process_dict = {'name': name, 'cpu': cpu, 'memory': memory}
                result.append(process_dict)
            except:
                pass

    return result


def to_int(value):
    number = re.compile('(\d+)')

    try:
        _int = number.search(value).group(1)
    except:
        _int = 0

    return int(_int)


# Removes the letters from a string
# From 24.5MB -> 24.5 -> used in the progress width
def clean_string(variable):

    if isinstance(variable, int)\
    or isinstance(variable, float)\
    or isinstance(variable, long):
        
        variable = float(variable) if not isinstance(variable, float) else variable

        return variable

    else:

        value_regex = re.compile(r'\d+[\.,]\d+') 
        extracted_value = value_regex.findall(variable)

        if len(extracted_value) > 0:
            extracted_value = extracted_value[0]
            extracted_value.replace(",",".")
            extracted_value = float(extracted_value)
        else:
            extracted_value = 0

        return extracted_value


# Used in the charts, where a disk drive could be with several slashes
def clean_slashes(string):
    return re.sub('[^A-Za-z0-9]+', '', string).strip().lower()


def get_key(dictionary, key):
    try: 
        value = dictionary[key]
    except:
        value = ''
        
    return value

# Used in Alerts - Not Sending Data
@register.filter
def add_spaces(value):
    if value != 'CPU':
        return re.sub(r"(?<=\w)([A-Z])", r" \1", value)

    return value

def dehumanize(value):

    values_dict = {
            "more_than": "&gt;",
            "less_than": "&lt;",
            "minute": "1 minute",
            "week": "1 week",
            "month": "1 month",
            "all": "All",
            "five_minutes": "5 minutes",
            "fifteen_minutes": "15 minutes"
            }

    try:
        _value = values_dict[value]
    except: 
        _value = ''

    
    return _value

def empty_if_none(value):
    if value in ['None', 'none', None, False, 'False']:
            return ""

    return value



class StripspacesNode(template.base.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return re.sub(r'\s+', '', (self.nodelist.render(context).strip()))

def stripspaces(parser, token):
    nodelist = parser.parse(('endstripspaces',))
    parser.delete_first_token()
    return StripspacesNode(nodelist)


 
def percentage(value, total):  
    try:  
        return "%.2f%%" % ((float(value) / float(total)) * 100)  
    except ValueError:  
        return ''  




register.tag('stripspaces', stripspaces)
register.filter('to_int', to_int)
register.filter('clean_slashes', clean_slashes)
register.filter('clean_string', clean_string)
register.filter('get_key', get_key)
register.filter('dehumanize', dehumanize)
register.filter('empty_if_none', empty_if_none)
register.filter('percentage', percentage) 
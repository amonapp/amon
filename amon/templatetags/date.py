from datetime import datetime
from django import template
from collections import OrderedDict
import re
from amon.utils.dates import (
    dateformat_local,
    datetimeformat_local,
    dateformat,
    timeformat,
    day_local, 
    time_local,
    dateformatcharts_local
)

register = template.Library()

def date_to_js(value, format='%Y, %m, %d, %H, %M'):
    # Converts unixtime to a javascript Date list
    _ = datetime.utcfromtimestamp(value)
    js_time_list = _.strftime(format).split(',')
    # Substract one month in js January is 0, February is 1, etc.
    js_time_list[1] = str(int(js_time_list[1])-1) 

    return ",".join(js_time_list) 


def extract_days_from_unixdate(value, days):
    day = 86400 # 1 day in seconds

    return value-(day*days)

def add_days_to_unixdate(value, days):
    day = 86400 # 1 day in seconds

    return value+(day*days)

def days_remaining(value):
    today = datetime.utcnow()
    remaining = value-today.date()
    try:
        remaining = value-today.date()
        remaining_days = remaining.days
    except:
        remaining_days = None

    return remaining_days


"""Convert seconds to human readable interval back and forth."""


interval_dict = OrderedDict([("Y", 365*86400),  # 1 year
                             ("M", 30*86400),   # 1 month
                             ("W", 7*86400),    # 1 week
                             ("D", 86400),      # 1 day
                             (" hours", 3600),       # 1 hour
                             (" minutes", 60),         # 1 minute
                             ("s", 1)])         # 1 second


@register.filter
def seconds_to_human(seconds):
    """Convert seconds to human readable format like 1M.

    :param seconds: Seconds to convert
    :type seconds: int

    :rtype: int
    :return: Human readable string
    """
    seconds = int(seconds)
    string = ""
    for unit, value in interval_dict.items():
        subres = seconds / value
        if subres:
            seconds -= value * subres
            string += str(subres) + unit
    return string




register.filter('time', timeformat)
register.filter('date_to_js', date_to_js)
register.filter('date', dateformat)
register.filter('date_local', dateformat_local)
register.filter('day_local', day_local)
register.filter('time_local', time_local)
register.filter('datetime_local', datetimeformat_local)
register.filter('datetimecharts_local', dateformatcharts_local)
register.filter('extract_days_from_unixdate', extract_days_from_unixdate)
register.filter('add_days_to_unixdate', add_days_to_unixdate)
register.filter('days_remaining', days_remaining)

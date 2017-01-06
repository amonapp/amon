from __future__ import division
import calendar
import pytz

from datetime import datetime, time, timedelta
from pytz import timezone
from operator import itemgetter

# Gets the UTC unix timestamp for 1800 before now
def utc_delta_from_now(period=1800):
    now = datetime.utcnow()
    now_unix = datetime_to_unixtime(now)
    
    delta = now_unix-period

    return delta


def expire_date(days=30):
    date_now = datetime.utcnow()
    expires_at = date_now + timedelta(days=days)

    return expires_at


def localtime_utc_timedelta(tz='UTC'):
    local_timezone = timezone(tz)
    local_time = datetime.now(local_timezone)

    is_dst = False # Check the local timezone for Daylight saving time
    if local_time.dst():
        is_dst = True

    naive_local_time = local_time.replace(tzinfo=None)

    # Return 0 for UTC
    if tz == 'UTC':
        return ('positive', 0)

    # timedelta betweeen the local timezone and UTC
    td = local_timezone.utcoffset(naive_local_time, is_dst=is_dst)
    offset = (td.microseconds + (td.seconds + td.days * 24 * 3600)* 10**6 ) / 10.0**6

    if offset < 0:
        # Negative timedelta is actually an UTC+ timezone
        offset = -offset
        offset_list = ('negative', int(offset))
    else:
        offset_list = ('positive', int(offset))

    return offset_list


# Converts date strings: '17:46' to an UTC datetime object for today -> 31-07-2011-17:46 or 1438936491
def time_to_utc_today(timestring, format="%H:%M", tz='UTC', to_utc=None):
    formated_time = datestring_to_utc_datetime(timestring, format=format)

    timezone = pytz.timezone(tz)
            
    today = datetime.now(timezone).date()
    time_datetime_obj = datetime.combine(today, time(formated_time.hour, formated_time.minute))

    if to_utc:
        time_datetime_obj = datetime_to_unixtime(time_datetime_obj)
    
    return time_datetime_obj

# Converts date strings: '31-07-2011-17:46' to an UTC datetime object using the
def datestring_to_utc_datetime(datestring, format="%d.%m.%Y-%H:%M", tz='UTC'):

    _datetime = datetime.strptime(datestring, format)

    local_timezone = timezone(tz)
    
    # Adjust for Daylight savings time
    local_datetime = local_timezone.localize(_datetime)
    utc_datetime =  local_datetime.astimezone(pytz.UTC)

    return utc_datetime

def unixtime_to_midnight(unixtime):
    dt = datetime.fromtimestamp(unixtime)
    midnight = time(0)
    
    return datetime.combine(dt.date(), midnight)


def unixtime_to_datetime_utc(unixtime):
    return datetime.fromtimestamp(unixtime, tz=pytz.UTC)

def unixtime_to_datetime(unixtime):
    return datetime.fromtimestamp(unixtime)
    
# Internal function, always pass UTC date objects
# Converts datetime objects to unix integers
def datetime_to_unixtime(datetime):
    return int(calendar.timegm(datetime.timetuple()))

# Converts date string to unix UTC time
def datestring_to_utc_unixtime(datestring):
    datetime_object = datestring_to_utc_datetime(datestring)
    
    return datetime_to_unixtime(datetime_object)



def utc_unixtime_to_localtime(unixtime, tz='UTC'):
    local_timezone = timezone(tz)
    
    unixtime = float(unixtime)
    utc = pytz.UTC
    utc_datetime = utc.localize(datetime.utcfromtimestamp(unixtime))
    local_datetime = utc_datetime.astimezone(local_timezone)

    local_unix_datetime = datetime_to_unixtime(local_datetime)
    local_unix_datetime = int(local_unix_datetime)

    return local_unix_datetime

# Used in the collector, saves all the data in UTC
def unix_utc_now():
    d = datetime.utcnow()
    _unix = calendar.timegm(d.utctimetuple())

    return _unix

def utc_now_to_localtime(tz='UTC'):
    now = unix_utc_now()
    local_unix_time = utc_unixtime_to_localtime(now, tz)
    local_unix_time = int(local_unix_time)

    return local_unix_time

 
def dateformat(value, format='%d.%m.%Y'):
    # Converts unix time to a readable date format
    try:
        _ = datetime.utcfromtimestamp(value)
        return _.strftime(format)
    except:
        return None


# Used in the alert emails
def time_local(value, tz='UTC',  format='%H:%M'):
    value = utc_unixtime_to_localtime(value, tz=tz)

    return dateformat(value, format)

# Used in the alert emails
def day_local(value, tz='UTC',  format='%d.%m.%Y'):
    value = utc_unixtime_to_localtime(value, tz=tz)

    return dateformat(value, format)


# Localized unix timestamp
def dateformat_local(value, format='%d-%m-%Y-%H:%M'):
    result = None

    try:
        value = utc_unixtime_to_localtime(value)
    except:
        value = None

    if value:
        result = dateformat(value, format)
    

    return result

def dateformatcharts_local(value, tz='UTC',format="%d.%m.%Y-%H:%M"):
    result = None

    try:
        value = utc_unixtime_to_localtime(value, tz=tz)
    except:
        value = None

    if value:
        result = dateformat(value, format)

    return result

# Localized unix timestamp
def datetimeformat_local(value, tz='UTC', format='%d.%m.%Y-%H:%M:%S'):
    result = None

    try:
        value = utc_unixtime_to_localtime(value, tz=tz)
    except:
        value = None

    if value:
        result = dateformat(value, format)

    return result

def timeformat(value, format='%H:%M'):
    # Converts unix time to a readable 24 hour-minute format
    _ = datetime.utcfromtimestamp(value)
    return _.strftime(format)


def timedelta_total_seconds(td):
    return int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)


def timezone_choices():

    TIMEZONE_CHOICES = []

    for timezone in pytz.common_timezones:
        now = datetime.now(pytz.timezone(timezone))
        offset = now.strftime("%z")
        TIMEZONE_CHOICES.append({"timezone": timezone,
            "offset": int(offset),
            "value": "(GMT{0}) {1}".format(offset, timezone)})



    sorted_timezones = sorted(TIMEZONE_CHOICES, key=itemgetter('offset'))

    return sorted_timezones
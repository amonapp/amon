from __future__ import division
from amon.core import settings
from datetime import datetime
import calendar
from pytz import timezone
import pytz
import time

def localtime_utc_timedelta(_timezone=None):
    _timezone = _timezone if _timezone else settings.TIMEZONE
    _timezone = 'Europe/Sofia' 
    is_dst = time.localtime().tm_isdst # Daylight saving time
    is_dst = True if is_dst == 1 else False
    
    local_timezone = timezone(_timezone)
    local_time = datetime.now(local_timezone)
    naive_local_time = local_time.replace(tzinfo=None)
    
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


# Converts date strings: '31-07-2011-17:46' to an UTC datetime object using the
# timezone in the config file
# The _timezone parameter is used only in the test suite
def datestring_to_utc_datetime(datestring, format="%d-%m-%Y-%H:%M", _timezone=None):
    _timezone = _timezone if _timezone else settings.TIMEZONE
    _datetime = datetime.strptime(datestring, format)
    local_timezone = timezone(_timezone)
    
    # Adjust for Daylight savings time
    local_datetime = local_timezone.localize(_datetime)
    utc_datetime =  local_datetime.astimezone(pytz.UTC)

    return utc_datetime
    
# Internal function, always pass UTC date objects
# Converts datetime objects to unix integers
def datetime_to_unixtime(datetime):
    return int(calendar.timegm(datetime.timetuple()))

# Converts date string to unix UTC time
def datestring_to_utc_unixtime(datestring):
    datetime_object = datestring_to_utc_datetime(datestring)
    
    return datetime_to_unixtime(datetime_object)

def utc_unixtime_to_localtime(unixtime, _timezone=None):
    _timezone = _timezone if _timezone else settings.TIMEZONE
    local_timezone = timezone(_timezone)
    
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

def utc_now_to_localtime(_timezone=None):
    _timezone = _timezone if _timezone else settings.TIMEZONE
    now = unix_utc_now()
    local_unix_time = utc_unixtime_to_localtime(now, _timezone)

    return local_unix_time

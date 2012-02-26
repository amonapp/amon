import datetime
import calendar

def unix_utc_now():
    d = datetime.datetime.utcnow()
    _unix = calendar.timegm(d.utctimetuple())

    return _unix




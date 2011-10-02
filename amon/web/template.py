from jinja2 import Environment, FileSystemLoader
from settings import TEMPLATES_DIR
from datetime import datetime, time
import re


env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def age(from_date, since_date = None, target_tz=None, include_seconds=False):
    '''
    Returns the age as a string
    '''
    if since_date is None:
        since_date = datetime.now(target_tz)
    
    distance_in_time = since_date - from_date
    distance_in_seconds = int(round(abs(distance_in_time.days * 86400 + distance_in_time.seconds)))
    distance_in_minutes = int(round(distance_in_seconds/60))

    if distance_in_minutes <= 1:
        if include_seconds:
            for remainder in [5, 10, 20]:
                if distance_in_seconds < remainder:
                    return "less than %s seconds" % remainder
            if distance_in_seconds < 40:
                return "half a minute"
            elif distance_in_seconds < 60:
                return "less than a minute"
            else:
                return "1 minute"
        else:
            if distance_in_minutes == 0:
                return "less than a minute"
            else:
                return "1 minute"
    elif distance_in_minutes < 45:
        return "%s minutes" % distance_in_minutes
    elif distance_in_minutes < 90:
        return "about 1 hour"
    elif distance_in_minutes < 1440:
        return "about %d hours" % (round(distance_in_minutes / 60.0))
    elif distance_in_minutes < 2880:
        return "1 day"
    elif distance_in_minutes < 43220:
        return "%d days" % (round(distance_in_minutes / 1440))
    elif distance_in_minutes < 86400:
        return "about 1 month"
    elif distance_in_minutes < 525600:
        return "%d months" % (round(distance_in_minutes / 43200))
    elif distance_in_minutes < 1051200:
        return "about 1 year"
    else:
        return "over %d years" % (round(distance_in_minutes / 525600))


# Custom filters
def time_in_words(value):
	'''
	Usage: {{ my_date_variable|time_in_words }}
	'''
	# if DateTimeFiled() or datetime.datetime variable
	try:
		time_ago = age(value)
	except:
		null_time = time()
		time_ago = age(datetime.combine(value, null_time))

	return time_ago

def dateformat(value, format='%d-%m-%Y-%H:%M'):
	# Converts unix time to a readable date format
	_ = datetime.fromtimestamp(value)
	return _.strftime(format)

def timeformat(value, format='%H:%M'):
	# Converts unix time to a readable 24 hour-minute format
	_ = datetime.fromtimestamp(value)
	return _.strftime(format)

def to_int(value):
	number = re.compile('(\d+)')
	
	try:
		_int = number.search(value).group(1)
	except:
		_int = 0

	return _int

def render(*args, **kwargs):
		
	env.filters['time'] = timeformat
	env.filters['date'] = dateformat
	env.filters['to_int'] =  to_int
	env.filters['time_in_words'] = time_in_words 

	if 'name' in kwargs:
		template = env.get_template(kwargs['name'])
	else:
		template = env.get_template('blank.html')

	return template.render(*args, **kwargs)


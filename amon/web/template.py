from jinja2 import Environment, FileSystemLoader
from settings import TEMPLATES_DIR
from datetime import datetime, time
import re
import string


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

# Removes the letters from a string
def clean_string(var):
	whitelist = string.digits + string.punctuation
	new_string = ''
	if not isinstance(var, int) and not isinstance(var, float):
		for char in var:
			if char in whitelist:
				new_string += char
	else:
		return var

	return new_string


def progress_width(value, total, container_type='full'):

	if container_type == 'full': 
		container_width = 500
	elif container_type == 'medium':
		container_width = 245
	else:
		container_width = 145

	value = clean_string(value)
	total = clean_string(total)

	percentage = float(value)/float(total) * 100
	progress_width = container_width/100 * percentage

	return '{0}px'.format(int(progress_width))


class RecursiveDict(object):

	def __init__(self):
		self.html = ''

	def walk_dict(self, d,depth=0):
		for k,v in sorted(d.items(),key=lambda x: x[0]):
			if isinstance(v, dict):
				# Continue the recursion only if the dictionary is not empty
				if v:
					self.html += '<ul class="level-{0}">'.format(depth)
					# strip the mongo variable
					if k != 'data':
						self.html += '<li><span class="key">{0}</span>'.format(k)
					self.walk_dict(v,depth+1)
					self.html += '</li>'
					self.html += '</ul>'
			else:
				if v and k != 'occurrence':
					self.html += '<li><span class="key_inner">{0}:</span><span class="value_inner">{1}</span></li>'.format(k,v)


def exceptions_dict(dict):
	dict_recursion = RecursiveDict()
	dict_recursion.walk_dict(dict)
	
	return dict_recursion.html



def render(*args, **kwargs):

	env.filters['time'] = timeformat
	env.filters['date'] = dateformat
	env.filters['to_int'] =  to_int
	env.filters['time_in_words'] = time_in_words 
	env.filters['progress_width'] = progress_width
	env.filters['exceptions_dict'] = exceptions_dict

	if 'name' in kwargs:
		template = env.get_template(kwargs['name'])
	else:
		template = env.get_template('blank.html')

	return template.render(*args, **kwargs)


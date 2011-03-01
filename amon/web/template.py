from jinja2 import Environment, FileSystemLoader
from settings import TEMPLATES_DIR
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
from datetime import datetime
import re

# Custom filters
def dateformat(value, format='%d-%m-%Y / %H:%M'):
	_ = datetime.fromtimestamp(value)
	return _.strftime(format)

def timeformat(value, format='%H:%M'):
	_ = datetime.fromtimestamp(value)
	return _.strftime(format)

def to_int(value):
	number = re.compile('(\d+)')

	return number.search(value).group(1)

def render(*args, **kwargs):
		
	env.filters['time'] = timeformat
	env.filters['date'] = dateformat
	env.filters['to_int'] =  to_int

	if 'name' in kwargs:
		template = env.get_template(kwargs['name'])
	else:
		template = env.get_template('blank.html')

	return template.render(*args, **kwargs)


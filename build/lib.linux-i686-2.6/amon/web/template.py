from jinja2 import Environment, FileSystemLoader
from settings import TEMPLATES_DIR
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
from datetime import datetime


# Custom filters
def dateformat(value, format='%d-%m-%Y / %H:%M'):
	_ = datetime.fromtimestamp(value)
	return _.strftime(format)



def render(*args, **kwargs):
		

	env.filters['date'] = dateformat

	if 'name' in kwargs:
		template = env.get_template(kwargs['name'])
	else:
		template = env.get_template('blank.html')

	return template.render(*args, **kwargs)


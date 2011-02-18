from jinja2 import Environment, FileSystemLoader
from settings import TEMPLATES_DIR
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def render(*args, **kwargs):
    
    if 'name' in kwargs:
        template = env.get_template(kwargs['name'])
    else:
        template = env.get_template('blank.html')

    return template.render(*args, **kwargs)
    

# References 
# http://code.djangoproject.com/browser/django/trunk/setup.py 
#!/usr/bin/env python
from amonlite import __version__
import os

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
amon_dir = 'amonlite'

for dirpath, dirnames, filenames in os.walk(amon_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

sdict = {
    'name' : 'amonlite',
    'version' : __version__,
    'description' : 'Elegant server and web application monitoring toolkit',
    'long_description' : 'Elegant server and web application monitoring toolkit',
    'url': 'https://github.com/martinrusev/amonlite',
    'author' : 'Martin Rusev',
    'author_email' : 'martinrusev@live.com',
    'keywords' : ['Amon', 'monitoring', 'logging', 'exception handling'],
    'license' : 'GPL',
    'packages' : packages,
    'data_files' : data_files,
    'install_requires': 
    [
        'pymongo==2.3',
        'tornado==2.4',
        'formencode==1.2.4',
        'Jinja2==2.6',
		'pip',
        'pytz'
    ]
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)

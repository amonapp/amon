# References 
# http://code.djangoproject.com/browser/django/trunk/setup.py 
#!/usr/bin/env python
from amonone import __version__
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
amonone_dir = 'amonone'

for dirpath, dirnames, filenames in os.walk(amonone_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])


sdict = {
    'name' : 'amonone',
    'version' : __version__,
    'long_description' : read('README.rst'),
    'author' : 'Martin Rusev',
    'author_email' : 'martin@amon.cx',
    'packages' : packages,
	'data_files' : data_files,
	'install_requires': 
	[
        'pymongo>=2.5.2',
		'tornado>=3.1',
		'formencode==1.2.6',
        'Jinja2',
        'mailtools==2.1',
        'pytz',
		'pip',
        'twilio'
    ],
   }

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(**sdict)

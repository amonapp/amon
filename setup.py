# References 
# http://code.djangoproject.com/browser/django/trunk/setup.py 
#!/usr/bin/env python
from amon import __version__
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

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
amon_dir = 'amon'

for dirpath, dirnames, filenames in os.walk(amon_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])


sdict = {
    'name' : 'Amon',
    'version' : __version__,
    'description' : 'Lightweight architecture monitoring tool',
    'long_description' : 'Lightweight architecture monitoring tool',
    'url': 'http://amon.martinrusev.net',
    'author' : 'Martin Rusev',
    'author_email' : 'martinrusev@live.com',
    'keywords' : ['Amon', 'monitoring'],
    'license' : 'GPL',
    'packages' : packages,
	'data_files' : data_files,
	'install_requires': 
	[
        'redis',
		'cherrypy>=3.1',
        'Jinja2>=2.4'
    ],
    'classifiers' : [
    'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
}

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(**sdict)

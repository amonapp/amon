#!/usr/bin/env python
from amon import __version__

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
    'packages' : ['amon','amon.web'],
	'package_data' : {'amon.web': ['css/*.css', 'images/*']},
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

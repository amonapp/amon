=============================================================
Amon - developer friendly system monitoring and logging tool
=============================================================

Introduction
=============

Amon tries to solve two very common problems for web application developers:


**1. System monitoring**


When we deploy our web applications it's important to know how much 
server resources they use over time, so that we can improve and optimize them.
On other hand installing a sophisticated server monitoring application looks
like overkill, if your app is not that big and probably lives on a single server.



**2. Language agnostic logging**


Installation
================

1. Download the tarball and install the package with ``python setup.py install``

2. Copy the system info collect daemon from ``contrib/amon`` to ``/etc/init.d/amon``

3. Make it executable with ``chmod +x /etc/init.d/amon`` and then start the daemon with ``invoke-rc.d/amon start``


Installing Mongodb
==================

Amon stores the system information in a Mongo database. In this section I will cover just the basics of
how to install and run a mongo instance. You can find much more details at http://mongodb.org

1. We need to create 3 directories for Mongo: - 
    
    ::

        mkdir /usr/local/mongodb - the main directory
        mkdir /usr/local/mongodb/data - for the database
        mkdir /usr/local/mongodb/bin - for the mongo executables
        touch /var/log/mongodb.log - the mongodb log file


2. Download Mongo from http://www.mongodb.org/downloads and copy the ``mongod`` file to ``/usr/local/mongodb/bin``

3. Copy the Mongo init script from ``contrib/mongodb`` to ``/etc/init/mongodb.conf``

4. Start the database with ``start mongodb`` 


Requirements
=============

Python 2.5+

pymongo >=1.1

CherryPy >=3.2

Jinja2 >=2.5

MongoDB

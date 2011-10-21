from template import render
import cherrypy
from pymongo import DESCENDING, ASCENDING 
from datetime import datetime, timedelta
from amon.backends.mongodb import MongoBackend
from amon.web.utils import (
		datestring_to_unixtime,
		datetime_to_unixtime,
		) 

from amon.core import settings
from amon.system.utils import get_disk_volumes, get_network_interfaces

class Base(object):

	def __init__(self):
		self.mongo = MongoBackend()
		self.now = datetime.now()


class Dashboard(Base):

	@cherrypy.expose
	def index(self):
		
		last_check = {}
		process_check = {}
		active_system_checks = settings.SYSTEM_CHECKS
		active_process_checks = settings.PROCESS_CHECKS
		
		# Get the first element from the settings - used for the last check date in the template
		system_check_first = active_system_checks[0]
		process_check_first = active_process_checks[0]

		try:
			for check in active_system_checks:
				row = self.mongo.get_collection(check)
				last_check[check] = row.find(limit=1).sort('time', DESCENDING)[0]
		except Exception, e:
			last_check = False
			raise e

		for check in active_process_checks:
			row = self.mongo.get_collection(check)
			process_check[check] = row.find(limit=1).sort('time', DESCENDING)[0]


		return render(name="dashboard.html",
					current_page='dashboard',
					last_check=last_check,
					process_check=process_check,
					system_check_first=system_check_first,
					process_check_first=process_check_first
					)

	# Terminate the server
	# TODO - more secure way to do it or find a way to deal with the cherrypy daemon nonsense
	@cherrypy.expose
	def exit(self):
		import sys
		sys.exit(1)

class System(Base):

	def __init__(self):
		super(System, self).__init__()
		self.now = datetime.now()


	@cherrypy.expose
	def index(self, *args, **kwargs):

		date_from = kwargs.get('date_from', False)
		date_to = kwargs.get('date_to', False)
		active_tab = kwargs.get('tab', 'day')

		if date_from:
			date_from = datestring_to_unixtime(date_from)
		# Default - 24 hours period
		else:
			day = timedelta(hours=24)
			yesterday = self.now - day

			date_from = datetime_to_unixtime(yesterday)
		
		if date_to:
			date_to = datestring_to_unixtime(date_to)
		else:
			date_to = datetime_to_unixtime(self.now)

		
		checks = {}
		active_checks = settings.SYSTEM_CHECKS
		try:
			for check in active_checks:
				row = self.mongo.get_collection(check)
				checks[check] = row.find({"time": {"$gte": date_from}}).sort('time', ASCENDING)
		except Exception, e:
			checks = False
			raise e

		if checks != False:
			network = []
			network_interfaces = []
			
			disk = []
			volumes = []
			
			if 'network' in active_checks:
				for check in checks['network']:
					network.append(check)	

				_interfaces = get_network_interfaces()
				for interface in _interfaces:
					if interface not in network_interfaces:
						network_interfaces.append(interface)

			if 'disk' in active_checks:
				for check in checks['disk']:
					disk.append(check)
			
				_volumes = get_disk_volumes()
				for volume in _volumes:
					if volume not in volumes:
						volumes.append(volume)

			return render(name='system.html',
						  current_page='system',
						  checks=checks,
						  network=network,
						  network_interfaces=network_interfaces,
						  volumes=volumes,
						  disk=disk,
						  active_tab=active_tab,
						  date_from=date_from,
						  date_to=date_to
						  )
		
class Processes(Base):

	def __init__(self):
		super(Processes, self).__init__()
		self.current_page = 'processes'
		self.processes = settings.PROCESS_CHECKS

	@cherrypy.expose
	def index(self, *args, **kwargs):
		day = timedelta(hours=24)
		_yesterday = self.now - day

		date_from = kwargs.get('date_from', False)
		date_to = kwargs.get('date_to', False)

		if date_from:
			date_from = datestring_to_unixtime(date_from)
		else:
			date_from = datetime_to_unixtime(_yesterday)
		
		if date_to:
			date_to = datestring_to_unixtime(date_to)
		else:
			date_to = datetime_to_unixtime(self.now)

		
		process_data = {}
		for process in self.processes:
			row = self.mongo.get_collection(process)
			process_data[process] = row.find({"time": {"$gte": date_from, '$lte': date_to}})\
					.sort('time', ASCENDING)
		

		return render(name='processes.html',
					  current_page=self.current_page,
					  processes=self.processes,
					  process_data=process_data,
					  date_from=date_from,
					  date_to=date_to
					 )


class Settings(Base):
	
	def __init__(self):
		super(Settings, self).__init__()
		self.current_page = 'settings'

	@cherrypy.expose
	def index(self):

		return render(name='settings.html',
					  current_page=self.current_page
					  )

	@cherrypy.expose
	def cleanup(self):
		return render(name='settings/cleanup.html',
					  current_page=self.current_page,
					  current_tab='cleanup'
					  )

	@cherrypy.expose
	def delete_exceptions(self):
		row = self.mongo.get_collection('exceptions') 
		row.remove()

		raise cherrypy.HTTPRedirect("/settings")	

	@cherrypy.expose
	def delete_logs(self):
		row = self.mongo.get_collection('logs')
		row.remove()
		
		raise cherrypy.HTTPRedirect("/settings")	

class Exceptions(Base):
	
	def __init__(self):
		super(Exceptions, self).__init__()
		self.current_page = 'exceptions'

	@cherrypy.expose
	def index(self):
		
		row = self.mongo.get_collection('exceptions') 
		
		exceptions = row.find().sort('last_occurrence', DESCENDING)

		return render(name='exceptions.html',
					  exceptions=exceptions,
					  current_page=self.current_page
					  )


class Logs(Base):

	def __init__(self):
		super(Logs, self).__init__()
		self.current_page = 'logs'

	@cherrypy.expose
	def index(self, *args, **kwargs):

		filter = kwargs.get('filter', {})
		# If there is only one parameter - convert it to list
		if isinstance(filter, unicode):
			filter = [filter]
		if filter:
			filter_params = [{'level': x} for x in filter]
			filter_query = {"$or" : filter_params}
		else:
			filter_query = {}


		row = self.mongo.get_collection('logs') 
		
		logs = row.find(filter_query).sort('time', DESCENDING)
 
		return render(name='logs.html',
					 current_page=self.current_page,
					 logs=logs,
					 filter=filter
					 )






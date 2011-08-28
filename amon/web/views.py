from template import render
import cherrypy
from amon.backends.mongodb import MongoBackend
from pymongo import DESCENDING, ASCENDING 
from datetime import datetime, timedelta
from utils import datestring_to_unixtime, datetime_to_unixtime  
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
		active_checks = settings.SYSTEM_CHECKS

		try:
			for check in active_checks:
				row = self.mongo.get_collection(check)
				last_check[check] = row.find(limit=1).sort('time', DESCENDING)[0]
		except Exception, e:
			last_check = False
			raise e

		return render(name="dashboard.html",
					current_page='dashboard',
					last_check=last_check
					)

class System(Base):

	def __init__(self):
		super(System, self).__init__()
		self.now = datetime.now()

		day = timedelta(hours=24)
		week = timedelta(days=7)
		month = timedelta(days=30)

		_yesterday = self.now - day
		_week_ago = self.now - week
		_month_ago = self.now - month

		self.yesterday = datetime_to_unixtime(_yesterday)
		self.week_ago = datetime_to_unixtime(_week_ago) 
		self.month_ago = datetime_to_unixtime(_month_ago) 


	@cherrypy.expose
	def index(self, *args, **kwargs):

		date_from = kwargs.get('date_from', False)
		active_tab = kwargs.get('tab', 'day')

		if date_from:
			date_from = datestring_to_unixtime(date_from)
		# Default - 24 hours period
		else:
			date_from = self.yesterday

		
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
						  week_ago=self.week_ago,
						  month_ago=self.month_ago,
						  active_tab=active_tab
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
		# Default - 24 hours period
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
		self.current_page = 'settings'

	@cherrypy.expose
	def index(self):

		return render(name='settings.html',
					  current_page=self.current_page
					  )





class Logs(Base):

	def __init__(self):
		self.current_page = 'logs'

	@cherrypy.expose
	def index(self):

		return render(name='logs.html',
					 current_page=self.current_page
					 )






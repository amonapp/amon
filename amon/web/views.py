from pymongo import DESCENDING, ASCENDING 
from datetime import datetime, timedelta
from amon.core import settings
from amon.web.template import render
from amon.backends.mongodb import MongoBackend
from amon.web.utils import datestring_to_unixtime,datetime_to_unixtime
from amon.system.utils import get_disk_volumes, get_network_interfaces
import tornado.web


class Base(tornado.web.RequestHandler):

	def initialize(self):
		self.mongo = MongoBackend()
		self.now = datetime.now()

		self.unread_col = self.mongo.get_collection('unread')
		self.unread_values = self.unread_col.find_one()
		
		super(Base, self).initialize()


	def write_error(self, status_code, **kwargs):
		error_trace = None
		
		if "exc_info" in kwargs:
		  import traceback
		  error_trace= ""
		  for line in traceback.format_exception(*kwargs["exc_info"]):
			error_trace += line 
		
		_template = render(template="error.html", 
				status_code=status_code,
				error_trace=error_trace,
				unread_values=None)

		self.write(_template)
	

class Dashboard(Base):

	def initialize(self):
		super(Dashboard, self).initialize()

	def get(self):
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
				# don't break the dashboard if the daemon is stopped
				last_check[check] = row.find({"last":{"$exists" : False}},limit=1).sort('time', DESCENDING)[0]
		except Exception, e:
			last_check = False
			raise e

		for check in active_process_checks:
			row = self.mongo.get_collection(check)
			process_check[check] = row.find({"last":{"$exists" : False}}, limit=1).sort('time', DESCENDING)[0]

		_template = render(template="dashboard.html",
				current_page='dashboard',
				last_check=last_check,
				process_check=process_check,
				system_check_first=system_check_first,
				process_check_first=process_check_first,
				unread_values=self.unread_values
				)

		self.write(_template)

class System(Base):

	def initialize(self):
		super(System, self).initialize()

	def get(self):

		date_from = self.get_argument('date_from', False)
		date_to = self.get_argument('date_to', False)

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
				checks[check] = row.find({"time": {"$gte": date_from,"$lt": date_to }}).sort('time', ASCENDING)
		except Exception, e:
			checks = False
			raise e

		try:
			row = self.mongo.get_collection('cpu')
			start_date = row.find_one()
		except Exception, e:
			start_date = False


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

			_template = render(template='system.html',
						  current_page='system',
						  checks=checks,
						  network=network,
						  network_interfaces=network_interfaces,
						  volumes=volumes,
						  disk=disk,
						  date_from=date_from,
						  date_to=date_to,
						  start_date=start_date,
						  unread_values=self.unread_values
						  )

			self.write(_template)

class Processes(Base):

	def initialize(self):
		super(Processes, self).initialize()
		self.current_page = 'processes'
		self.processes = settings.PROCESS_CHECKS

	def get(self):
		day = timedelta(hours=24)
		_yesterday = self.now - day

		date_from = self.get_argument('date_from', False)
		date_to = self.get_argument('date_to', False)

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
			process_data[process] = row.find({"time": {"$gte": date_from, '$lt': date_to}})\
					.sort('time', ASCENDING)
		

		_template = render(template='processes.html',
					  current_page=self.current_page,
					  processes=self.processes,
					  process_data=process_data,
					  date_from=date_from,
					  date_to=date_to,
					  unread_values=self.unread_values
					 )

		self.write(_template)


class Exceptions(Base):
	
	def initialize(self):
		super(Exceptions, self).initialize()
		self.current_page = 'exceptions'

	def get(self):
		
		row = self.mongo.get_collection('exceptions') 
		
		exceptions = row.find().sort('last_occurrence', DESCENDING)

		# Update unread count
		self.unread_col.update({"id": 1}, {"$set": {"exceptions": 0}})

		_template = render(template='exceptions.html',
					  exceptions=exceptions,
					  current_page=self.current_page,
					  unread_values=self.unread_values
					  )

		self.write(_template)

class Logs(Base):

	def initialize(self):
		super(Logs, self).initialize()
		self.current_page = 'logs'

	def get(self):

		# Update unread count
		self.unread_col.update({"id": 1}, {"$set": {"logs": 0}})
		
		row = self.mongo.get_collection('logs') 
		logs = row.find().sort('time', DESCENDING)
 

		_template =  render(template='logs.html',
					 current_page=self.current_page,
					 logs=logs,
					 unread_values=self.unread_values,
					 )
		
		self.write(_template)


	def post(self):
		level = self.get_arguments('level[]')
		filter = self.get_argument('filter', None)

		_query = {}
		if level:
			level_params = [{'level': x} for x in level]
			_query = {"$or" : level_params}

		if filter:
			_query['message'] = {'$regex': str(filter)}

		row = self.mongo.get_collection('logs') 
		
		logs = row.find(_query).sort('time', DESCENDING)

		_template = render(template='partials/logs_filter.html', 
				logs=logs)

		self.write(_template)

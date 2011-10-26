from pymongo import DESCENDING, ASCENDING 
from datetime import datetime, timedelta
from amon.backends.mongodb import MongoBackend
from amon.web.utils import (
		datestring_to_unixtime,
		datetime_to_unixtime,
		) 
from amon.system.utils import (
		get_disk_volumes, 
		get_network_interfaces
		)
from amon.core import settings
#from amon.web.template import render
from template import render

import tornado.ioloop
import tornado.web


class Base(tornado.web.RequestHandler):

	def initialize(self):
		self.mongo = MongoBackend()
		self.now = datetime.now()
		super(Base, self).initialize()

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
				last_check[check] = row.find(limit=1).sort('time', DESCENDING)[0]
		except Exception, e:
			last_check = False
			raise e

		for check in active_process_checks:
			row = self.mongo.get_collection(check)
			process_check[check] = row.find(limit=1).sort('time', DESCENDING)[0]

		rendered_template = render(template="dashboard.html",
				current_page='dashboard',
				last_check=last_check,
				process_check=process_check,
				system_check_first=system_check_first,
				process_check_first=process_check_first
				)

		self.write(rendered_template)


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

			rendered_template = render(template='system.html',
						  current_page='system',
						  checks=checks,
						  network=network,
						  network_interfaces=network_interfaces,
						  volumes=volumes,
						  disk=disk,
						  date_from=date_from,
						  date_to=date_to
						  )

			self.write(rendered_template)


import cherrypy
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
from amon.web.template import render

import tornado.ioloop
import tornado.web

from settings import PROJECT_ROOT


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




if __name__ == "__main__":

	import os
	
	app_settings = {
		"static_path": os.path.join(PROJECT_ROOT, "media"),
		"debug": True
	}

	application = tornado.web.Application([
		(r"/", Dashboard),
		(r"/media/(.*)", tornado.web.StaticFileHandler, {"path": app_settings['static_path']}),
	])

	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()

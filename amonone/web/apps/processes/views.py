from amonone.web.apps.core.baseview import BaseView
from tornado.web import authenticated
from datetime import timedelta
from amonone.web.apps.core.models import server_model
from amonone.web.apps.processes.models import process_model
from amonone.utils.dates import (
		utc_now_to_localtime, 
		datestring_to_utc_datetime,
		utc_unixtime_to_localtime,
		localtime_utc_timedelta,
		datetime_to_unixtime
)

class ProcessesView(BaseView):

	def initialize(self):
		self.current_page = 'processes'
		super(ProcessesView, self).initialize()

	@authenticated
	def get(self):
		date_from = self.get_argument('date_from', None)
		date_to = self.get_argument('date_to', None)
		daterange = self.get_argument('daterange', None)
		processes = self.get_arguments('process', None)


		 # Default 24 hours period
		day = timedelta(hours=24)
		default_to = self.now
		default_from = default_to - day

		if date_from:
			date_from = datestring_to_utc_datetime(date_from)
		else:
			date_from = default_from

		if date_to:
			date_to = datestring_to_utc_datetime(date_to)
		else:
			date_to = default_to

		date_from = datetime_to_unixtime(date_from)
		date_to = datetime_to_unixtime(date_to) 
		default_from = datetime_to_unixtime(default_from)
		default_to = datetime_to_unixtime(default_to) 

		process_data = process_model.get_process_data(processes, date_from, date_to)

		# Convert the dates to local time for display
		date_from = utc_unixtime_to_localtime(date_from)
		date_to = utc_unixtime_to_localtime(date_to)
		default_from = utc_unixtime_to_localtime(default_from)
		default_to = utc_unixtime_to_localtime(default_to)

		# Get the difference between UTC and localtime - used to display 
		# the ticks in the charts
		zone_difference = localtime_utc_timedelta()

		# Get the max date - utc, converted to localtime
		max_date = utc_now_to_localtime() 

		server = server_model.get_one()

		self.render('processes.html',	
				current_page=self.current_page,
				processes=processes,
				process_data=process_data,
				date_from=date_from,
				date_to=date_to,
				default_from=default_from,
				default_to=default_to,
				zone_difference=zone_difference,
				max_date=max_date,
				daterange=daterange,
				server=server
				)
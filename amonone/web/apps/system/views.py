from tornado.web import authenticated
from datetime import timedelta
from amonone.web.apps.core.baseview import BaseView
from amonone.web.apps.core.models import server_model
from amonone.web.apps.system.models import system_model
from amonone.utils.dates import ( 
	datestring_to_utc_datetime,
	datetime_to_unixtime,
	unix_utc_now,
	utc_unixtime_to_localtime,
	localtime_utc_timedelta,
	utc_now_to_localtime
)

class SystemView(BaseView):

	def initialize(self):
		self.current_page='system'
		super(SystemView, self).initialize()

	@authenticated
	def get(self):

		date_from = self.get_argument('date_from', None)
		date_to = self.get_argument('date_to', None)
		charts = self.get_arguments('charts', None)
	   
		daterange = self.get_argument('daterange', None)

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
	 	

		checks = system_model.get_system_data(charts, date_from, date_to)
		
		active_charts = charts if len(charts) > 0 else checks.keys()
	  
		first_check_date = system_model.get_first_check_date()

		default_from = datetime_to_unixtime(default_from)
		default_to = datetime_to_unixtime(default_to) 

		# Convert the dates to local time for display
		first_check_date = utc_unixtime_to_localtime(first_check_date)
		date_from = utc_unixtime_to_localtime(date_from)
		date_to = utc_unixtime_to_localtime(date_to)
		default_from = utc_unixtime_to_localtime(default_from)
		default_to = utc_unixtime_to_localtime(default_to)

		# Get the max date - utc, converted to localtime
		max_date = utc_now_to_localtime()
		
		# Get the difference between UTC and localtime - used to display 
		# the ticks in the charts
		zone_difference = localtime_utc_timedelta()

		server = server_model.get_one()


		self.render('system.html',
				charts=charts,
				active_charts=active_charts,
				checks=checks,
				daterange=daterange,
				date_from=date_from,
				date_to=date_to,
				default_from=default_from,
				default_to=default_to,
				first_check_date=first_check_date,
				zone_difference=zone_difference,
				max_date=max_date,
				server=server
				)
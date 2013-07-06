from tornado.web import authenticated
from amonone.web.apps.core.baseview import BaseView
from amonone.web.apps.core.models import server_model
from amonone.web.apps.dashboard.models import dashboard_model
from amonone.utils.dates import (
		utc_now_to_localtime, 
		datestring_to_utc_datetime,
		utc_unixtime_to_localtime,
		localtime_utc_timedelta,
		datetime_to_unixtime
)

class DashboardView(BaseView):

	def initialize(self):
		self.current_page='dashboard'
		super(DashboardView, self).initialize()

	@authenticated
	def get(self):

		snapshot_param = self.get_argument('snapshot', None)
		
		snapshot = None
		if snapshot_param:
			snapshot = datestring_to_utc_datetime(snapshot_param)
			snapshot = datetime_to_unixtime(snapshot)


		system_check = dashboard_model.get_system_check(snapshot)
		process_check = dashboard_model.get_process_check(snapshot)

		# Get the max date - utc, converted to localtime
		max_date = utc_now_to_localtime() 

		self.render("dashboard.html",
				system_check=system_check,
				process_check=process_check,
				max_date=max_date,
				snapshot=snapshot_param
				)
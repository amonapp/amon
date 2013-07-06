from formencode.validators import Invalid as InvalidForm
from tornado.web import authenticated
from amonone.web.apps.core.baseview import BaseView

from amonone.web.apps.settings.models import data_model
from amonone.web.apps.core.models import server_model
from amonone.utils.dates import utc_now_to_localtime, datestring_to_utc_datetime, datetime_to_unixtime
from amonone.web.apps.settings.forms import DataCleanupForm

class DataBaseView(BaseView):
	def initialize(self):
		self.current_page = 'settings:data'
		super(DataBaseView, self).initialize()

class DataView(DataBaseView):

	@authenticated
	def get(self):
		database_info = data_model.get_database_info()
		server_data = data_model.get_server_collection_stats()


		self.render('settings/data.html',
				database_info=database_info,
				server_data=server_data
				)

class DataDeleteSystemCollectionView(DataBaseView):

	@authenticated
	def get(self, server_id=None):
		server = server_model.get_by_id(server_id)
		data_model.delete_system_collection(server)

		self.redirect(self.reverse_url('settings_data'))

class DataDeleteProcessCollectionView(DataBaseView):

	@authenticated
	def get(self, server_id=None):
		server = server_model.get_by_id(server_id)
		data_model.delete_process_collection(server)

		self.redirect(self.reverse_url('settings_data'))


class DataCleanupProcessView(DataBaseView):

	@authenticated
	def get(self, server_id=None):
		errors =  self.session.get('errors',None)

		# Get the max date - utc, converted to localtime
		max_date = utc_now_to_localtime() 

		server = server_model.get_by_id(server_id)

		self.render('settings/data/process_cleanup.html',
				server=server,
				errors=errors,
				max_date=max_date)

	@authenticated
	def post(self, server_id=None):
		
		form_data = {
				"server": server_id,
				"date" : self.get_argument('date', None),         
		}

		try:
			DataCleanupForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			# Convert to unix utc
			date = datestring_to_utc_datetime(form_data['date'])
			date = datetime_to_unixtime(date)
			
			server = server_model.get_by_id(form_data['server'])

			data_model.cleanup_process_collection(server, date)

			self.redirect(self.reverse_url('settings_data'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			self.redirect(self.reverse_url('cleanup_process' ,server_id))


class DataCleanupSystemView(DataBaseView):

	@authenticated
	def get(self, server_id=None):
		errors =  self.session.get('errors',None)

		# Get the max date - utc, converted to localtime
		max_date = utc_now_to_localtime() 

		server = server_model.get_by_id(server_id)

		self.render('settings/data/system_cleanup.html',
				server=server,
				errors=errors,
				max_date=max_date)
	
	@authenticated
	def post(self, server_id=None):
		
		form_data = {
				"server": server_id,
				"date" : self.get_argument('date', None),         
		}

		try:
			DataCleanupForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')
		
			# Convert to unix utc
			date = datestring_to_utc_datetime(form_data['date'])
			date = datetime_to_unixtime(date)
			
			server = server_model.get_by_id(form_data['server'])

			data_model.cleanup_system_collection(server, date)

			self.redirect(self.reverse_url('settings_data'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data

			self.redirect(self.reverse_url('cleanup_system', server_id))
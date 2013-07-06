from formencode.validators import Invalid as InvalidForm
from tornado.web import authenticated
from amonone.web.apps.core.baseview import BaseView

from amonone.web.apps.alerts.models import alerts_model, alerts_group_model
from amonone.web.apps.core.models import server_model
from amonone.web.apps.settings.forms import ServerForm

class ServersBaseView(BaseView):
	def initialize(self):
		self.current_page = 'settings:servers'
		super(ServersBaseView, self).initialize()

class ServersView(ServersBaseView):

	@authenticated
	def get(self):
		errors =  self.session.get('errors',None)
		all_servers = server_model.get_all()

		servers = []
		if all_servers:
			for server in all_servers.clone():

				alert_group = server.get('alert_group', None)
				server['alert_group'] = alerts_group_model.get_by_id(alert_group)
			
				servers.append(server)

		self.render('settings/servers/view.html', 
				servers=servers)

class ServersDeleteView(ServersBaseView):

	@authenticated
	def get(self, param=None):
		server = server_model.get_by_id(param)

		alerts_model.delete_server_alerts(param)
		server_model.delete(param)
		
		self.redirect(self.reverse_url('settings_servers'))


class ServersUpdateView(ServersBaseView):


	@authenticated
	def get(self, param=None):
		errors =  self.session.get('errors',None)
		server = server_model.get_by_id(param)
		groups = alerts_group_model.get_all()

		self.delete_session_key('errors')

		self.render('settings/servers/edit.html', 
				server=server,
				groups=groups,
				errors=errors)

	@authenticated
	def post(self, param=None):
		self.check_xsrf_cookie()


		form_data = {
				"name": self.get_argument('name', ''),
				"notes": self.get_argument('notes', ''),
				"alert_group": self.get_argument('alert_group', ''),
				}

		try:
			valid_data = ServerForm.to_python(form_data)
			server_model.update(valid_data, param)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')

			self.redirect(self.reverse_url('settings_servers'))

		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data


			self.redirect(self.reverse_url('update_server', param))


class ServersAddView(ServersBaseView):

	@authenticated
	def get(self):
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)
		groups = alerts_group_model.get_all()

		self.delete_session_key('errors')

		self.render('settings/servers/add.html',
				groups=groups,
				errors=errors,
				form_data=form_data)

	@authenticated
	def post(self):
		self.check_xsrf_cookie()

		form_data = {
				"name": self.get_argument('name', ''),
				"notes": self.get_argument('notes', ''),
				"alert_group": self.get_argument('alert_group', ''),
				}

		try:
			valid_data = ServerForm.to_python(form_data)
			server_model.add(valid_data['name'],
			 	valid_data['notes'],
			  	valid_data['alert_group'])

			self.delete_session_key('errors')
			self.delete_session_key('form_data')

			self.redirect(self.reverse_url('settings_servers'))

		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data


			self.redirect(self.reverse_url('settings_servers_add'))
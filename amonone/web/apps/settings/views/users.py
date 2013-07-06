from formencode.validators import Invalid as InvalidForm
from tornado.web import authenticated
from amonone.web.apps.core.baseview import BaseView

from amonone.web.apps.auth.models import user_model
from amonone.web.apps.core.models import server_model
from amonone.web.apps.settings.forms import CreateUserForm

class BaseUsersView(BaseView):
	def initialize(self):
		self.current_page = 'settings:users'
		super(BaseUsersView, self).initialize()

class UsersView(BaseUsersView):

	@authenticated
	def get(self):
		users = user_model.get_all()
	
		all_servers = server_model.get_all()
		if all_servers:
			all_servers = dict((str(record['_id']), record['name']) for record in all_servers)
		
		self.render('/settings/users/view.html', 
				users=users,
				all_servers=all_servers)


class DeleteUserView(BaseUsersView):

	@authenticated
	def get(self, id=None):
		if self.current_user['type'] == 'admin':
			user_model.delete(id)
			self.redirect(self.reverse_url('settings_users'))


class EditUserView(BaseUsersView):

	@authenticated
	def get(self, id=None):
		user = user_model.get(id)
		all_servers = server_model.get_all()
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)

		self.delete_session_key('errors')
		self.delete_session_key('form_data')

		self.render('/settings/users/edit.html', 
				user=user,
				all_servers=all_servers,
				errors=errors,
				form_data=form_data)

	@authenticated
	def post(self, id):
		
		form_data = {
				"servers": self.get_arguments('servers[]',None)
		}

		# Remove all other values if all in the list
		if len(form_data['servers']) > 0:
			form_data['servers'] = ['all'] if 'all' in form_data['servers'] else form_data['servers']

		user_model.update(form_data, id)
		self.redirect(self.reverse_url('settings_users'))

class UpdatePasswordUserView(BaseUsersView):

	@authenticated
	def post(self, id):
		
		form_data = {
				"password" : self.get_argument('password', None),
		}
		if len(form_data['password']) > 0:
			user_model.update(form_data, id)
		self.redirect(self.reverse_url('settings_users'))		

class CreateUserView(BaseUsersView):

	@authenticated
	def get(self):
		all_servers = server_model.get_all()
		errors =  self.session.get('errors',None)
		form_data =  self.session.get('form_data',None)

		self.delete_session_key('errors')
		self.delete_session_key('form_data')


		self.render('settings/users/create.html',
				all_servers=all_servers,
				errors=errors,
				form_data=form_data)
	
	@authenticated
	def post(self):
		
		form_data = {
				"username": self.get_argument('username', None),
				"password" : self.get_argument('password', None),         
				"type": self.get_argument('type', None),
				"servers": self.get_arguments('servers[]',None)
		}

		try:
			CreateUserForm.to_python(form_data)

			self.delete_session_key('errors')
			self.delete_session_key('form_data')

			user_model.create_user(form_data)
			self.redirect(self.reverse_url('settings_users'))
		
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data

			self.redirect(self.reverse_url('settings_create_user'))
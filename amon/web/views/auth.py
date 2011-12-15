from amon.web.views.base import BaseView
from amon.web.forms import CreateUserForm
from amon.web.models import user_model
from formencode.validators import Invalid as InvalidForm


class LoginView(BaseView):

	def initialize(self):
		super(LoginView, self).initialize()


	def get(self):
		message =  self.session.get('message',None)
		errors =  self.session.get('errors',None)
		
		try:
			del self.session['errors']
		except:
			pass

		self.render('login.html', message=message, errors=errors)


	def post(self):
		form_data = {
				"username": self.get_argument('username', None),
				"password": self.get_argument('password', None),
				}


		user = user_model.check_user(form_data)

		if len(user) == 0:
			self.session['errors'] = "Invalid login details"
			self.redirect('/login')
		else:
			self.session['user'] = {'username': user['username'],
					'user_id': user['_id']}
			
			self.redirect('/')

class LogoutView(BaseView):

	def initialize(self):
		super(LogoutView, self).initialize()


	def get(self):
		try:
			del self.session['user']
		except:
			pass
		
		self.redirect('/login')

class CreateUserView(BaseView):

	def initialize(self):
		super(CreateUserView, self).initialize()


	def get(self):

		errors = self.session.get('errors', None)
		form_data = self.session.get('form_data', None)

		# This page is active only when there are no users in the system
		users = user_model.count_users()

		if users == 0:
			self.render('create_user.html', errors=errors, form_data=form_data)
		else:
			self.redirect('/login')
		

	def post(self):
		form_data = {
				"username": self.get_argument('username', None),
				"password": self.get_argument('password', None),
				}
		try:
			valid_data = CreateUserForm.to_python(form_data)
			user_model.create_user(valid_data)
			self.session['message'] = 'Account successfuly created. You can now log in'

			try:
				del self.session['errors']
				del self.session['form_data']
			except:
				pass

			self.redirect('/login')

		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data

			self.redirect('/create_user')





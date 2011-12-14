from amon.web.views.base import BaseView
from amon.web.template import render
from amon.web.forms import CreateUserForm
from amon.web.models import user_model
from formencode.validators import Invalid as InvalidForm


class LoginView(BaseView):

	def initialize(self):
		super(LoginView, self).initialize()


	def get(self):
		message =  self.session.get('message',None)
		errors =  self.session.get('errors',None)

		_template = render(template='login.html',
						message=message,
						errors=errors)

		self.delete_key(self.session.get('errors', None))
		self.delete_key(self.session.get('form_data', None))

		self.write(_template)


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
		self.delete_key(self.session.get('user', None))
		self.redirect('/login')

class CreateUserView(BaseView):

	def initialize(self):
		super(CreateUserView, self).initialize()


	def get(self):
		errors = self.session.get('errors', None)
		form_data = self.session.get('form_data', None)



		_template = render(template='create_user.html',
				errors=errors,
				form_data=form_data)

		self.write(_template)

	def post(self):
		form_data = {
				"username": self.get_argument('username', None),
				"password": self.get_argument('password', None),
				}
		try:
			valid_data = CreateUserForm.to_python(form_data)
			user_model.create_user(valid_data)
			self.session['message'] = 'Account successfuly created. You can now log in'


			self.delete_key(self.session.get('errors', None))
			self.delete_key(self.session.get('form_data', None))

			self.redirect('/login')

		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data

			self.redirect('/create_user')





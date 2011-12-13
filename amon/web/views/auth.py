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
		
		try:
			del self.session['errors']
			del self.session['message']
			self.save_session()
		except:
			pass

		
		self.write(_template)


	def post(self):
		form_data = {
			"username": self.get_argument('username', None),
			"password": self.get_argument('password', None),
		}
	   

		user = user_model.check_user(form_data)
		
		if len(user) == 0:
			self.session['errors'] = "Invalid login details"
			self.save_session()
			self.redirect('/login')
		else:
			self.session['user'] = {'username': user['username'],
									'user_id': user['_id']}
			self.save_session()
			self.redirect('/')

class LogoutView(BaseView):
	
	def initialize(self):
		super(LogoutView, self).initialize()


	def get(self):
		try:
			del self.session['user']
			self.save_session()
		except:
			pass

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
			self.save_session()
			
			try:
				del self.session['errors']
				del self.session['form_data']
				self.save_session()
			except:
				pass

			self.redirect('/login')

		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.session['form_data'] = form_data
			
			self.save_session()
			self.redirect('/create_user')
 




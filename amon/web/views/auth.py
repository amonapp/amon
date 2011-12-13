from amon.web.views.base import BaseView
from amon.web.template import render
from amon.web.forms import CreateUserForm
from formencode.validators import Invalid as InvalidForm
	


class LoginView(BaseView):

	def initialize(self):
		super(LoginView, self).initialize()


	def get(self):
		_template = render(template='login.html')
		self.write(_template)

class CreateUserView(BaseView):

	def initialize(self):
		super(CreateUserView, self).initialize()


	def get(self):
		try:
			print repr(self.session)
		except:
			pass
		_template = render(template='create_user.html')
		self.write(_template)

	def post(self):
		form_data = {
			"username": self.get_argument('username', None),
			"password": self.get_argument('password', None),
		}
		try:
			valid_data = CreateUserForm.to_python(form_data)
		except InvalidForm, e:
			self.session['errors'] = e.unpack_errors()
			self.save_session()
			self.redirect('/create_user')
 




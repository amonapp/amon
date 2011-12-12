from amon.web.views.base import BaseView
from amon.web.template import render

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
		_template = render(template='create_user.html')
		self.write(_template)




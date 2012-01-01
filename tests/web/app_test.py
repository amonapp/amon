from nose.tools import eq_
from tornado.testing import AsyncHTTPTestCase
from amon.web.server import application
from amon.core import settings

if settings.ACL == 'False':
	status_code = 200
else:
	status_code = 302 
	# redirect if acl is true


class TestWebApplication(AsyncHTTPTestCase):

	def get_app(self):
		return application

	def test_login(self):
		response = self.fetch('/login')
		eq_(response.code, 200)

	def test_logout(self):
		response = self.fetch('/logout')
		eq_(response.code, 200)

	def test_create_user(self):
		response = self.fetch('/create_user', follow_redirects=False)
		eq_(response.code, 302)

class TestPasswordProtected(AsyncHTTPTestCase):

	def get_app(self):
		return application

	def test_dashboard(self):
		response = self.fetch('/', follow_redirects=False)
		eq_(response.code, status_code)
	
	def test_logs(self):
		response = self.fetch('/logs', follow_redirects=False)
		eq_(response.code, status_code)

	def test_exceptions(self):
		response = self.fetch('/exceptions', follow_redirects=False)
		eq_(response.code, status_code)
	
	def test_processes(self):
		response = self.fetch('/processes', follow_redirects=False)
		eq_(response.code, status_code)
	
	def test_log_api(self):
		response = self.fetch('/api/log')
		eq_(response.code, status_code)

	def test_exception_api(self):
		response = self.fetch('/api/exception')
		eq_(response.code, status_code)


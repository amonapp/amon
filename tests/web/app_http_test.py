from nose.tools import eq_
from tornado.testing import AsyncHTTPTestCase
from amon.web.server import application

class TestWebApplication(AsyncHTTPTestCase):

	def get_app(self):
		return application

	def test_dashboard(self):
		response = self.fetch('/')
		eq_(response.code, 200)
	
	def test_logs(self):
		response = self.fetch('/logs')
		eq_(response.code, 200)

	def test_exceptions(self):
		response = self.fetch('/exceptions')
		eq_(response.code, 200)
	
	def test_processes(self):
		response = self.fetch('/processes')
		eq_(response.code, 200)
	
	def test_log_api(self):
		response = self.fetch('/api/log')
		eq_(response.code, 200)

	def test_exception_api(self):
		response = self.fetch('/api/exception')
		eq_(response.code, 200)



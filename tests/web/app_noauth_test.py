#from nose.tools import eq_
#from tornado.testing import AsyncHTTPTestCase
#from amon.web.server import application

#class TestNoAuth(AsyncHTTPTestCase):

	#def get_app(self):
		#return application

	#def test_dashboard(self):
		#response = self.fetch('/', follow_redirects=False)
		#eq_(response.code, 200)
	
	#def test_logs(self):
		#response = self.fetch('/logs', follow_redirects=False)
		#eq_(response.code, 302)

	#def test_exceptions(self):
		#response = self.fetch('/exceptions', follow_redirects=False)
		#eq_(response.code, 302)
	
	#def test_processes(self):
		#response = self.fetch('/processes', follow_redirects=False)
		#eq_(response.code, 302)
	

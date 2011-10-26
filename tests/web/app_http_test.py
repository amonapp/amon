import unittest
import requests
import subprocess
from nose.tools import eq_
#from time import sleep

class TestWebApplication(unittest.TestCase):

	url = 'http://127.0.0.1:2464/'
	
	# That is the only sane way to test a cherrypy application - you create a script, that starts the server 
	# and another one that stops it at the end of the suite
	
	#def setUp(self):
		#subprocess.Popen(['amon_start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
		#sleep(2)

	#def tearDown(self):
		#subprocess.Popen(['killall', '-v','amon_start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
		#sleep(2)

	def test_dashboard(self):
		page = requests.get(self.url)
		eq_(page.status_code, 200)

	def test_logs(self):
		page = requests.get(self.url+'logs')
		eq_(page.status_code, 200)

	def test_exceptions(self):
		page = requests.get(self.url+'exceptions')
		eq_(page.status_code, 200)
	
	def test_processes(self):
		page = requests.get(self.url+'processes')
		eq_(page.status_code, 200)

	
	# Only json requests
	def test_log_api(self):
		page = requests.get(self.url+'api/log')
		eq_(page.status_code, 405)

	def test_exception_api(self):
		page = requests.get(self.url+'api/exception')
		eq_(page.status_code, 405)




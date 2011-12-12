import unittest
from amon.web.views.base import BaseView
from amon.web.server import application
from tornado.httpclient import HTTPRequest 
from nose.tools import eq_

class DummyRequest(HTTPRequest):

	remote_ip = '127.0.0.1'

	def __init_(self):
		super(DummyRequest, self).__init__()

	def supports_http_1_1(self):
		return False

req = DummyRequest('/')

class TestSessionView(BaseView):

	def initialize(self):
		super(TestSessionView, self).initialize()


test_class = TestSessionView(application, req)

class SessionTest(unittest.TestCase):

	
	def test_session_add(self):
		test_class.session['key'] = 'value'
		eq_(test_class.session['key'], 'value')
		


		



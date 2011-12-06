import unittest
from amon.web.models import (
	CommonModel, 
	SystemModel
)
from nose.tools import eq_
from time import time


class TestCommonModel(unittest.TestCase):
	
	def setUp(self):
		self.model = CommonModel()
		self.model.mongo.database = 'amon_test'


	def test_unread(self):
		unread = self.model.get_unread_values()
		
		eq_(1,unread['id'])

		# Check if there is a log and exception field
		eq_(True, unread.has_key('logs'))
		eq_(True, unread.has_key('exceptions'))

class TestSystemModel(unittest.TestCase):


	def setUp(self):
		self.model = SystemModel()
		self.model.mongo.database = 'amon_test'


	def test_get_system_data(self):
		active_checks = ['cpu']
		# Delete everything in the cpu collection
		cpu = self.model.mongo.get_collection('cpu')
		cpu.remove()
		
		now = int(time())
		minute_ago = (now-60)
		two_minites_ago = (now-120)

		empty_result = self.model.get_system_data(active_checks, minute_ago, now)
		
		eq_(len(empty_result), 1) # Should return only the cpu field {cpu: pymongoobject}

		# Nothing in the cpu field
		for cpu in empty_result['cpu']:
			eq_(cpu, False)


		_from = {"system" : 1, "idle" : 98, "user" : 0, "time" : minute_ago}
		_from2 = {"system" : 1, "idle" : 98, "user" : 0, "time" : two_minites_ago}
		_to = {"system" : 1, "idle" : 98, "user" : 0, "time" : now}
		cpu.insert(_from)
		cpu.insert(_from2)
		cpu.insert(_to)

		result = self.model.get_system_data(active_checks, two_minites_ago, now)
		eq_(result['cpu'].count(), 3)

		result = self.model.get_system_data(active_checks, minute_ago, now)
		eq_(result['cpu'].count(), 2)

		# Cleanup the collection
		cpu.remove()

		


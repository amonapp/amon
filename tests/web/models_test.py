import unittest
from amon.web.models import (
	SystemModel,
	ProcessModel,
	LogModel,
	ExceptionModel,
	DashboardModel,
	UserModel,
	UnreadModel
)
from nose.tools import eq_
from time import time

now = int(time())
minute_ago = (now-60)
two_minutes_ago = (now-120)
import os
os.environ['AMON_ENV'] = 'test' # Switches the database to amon_test.

class TestUnreadModel(unittest.TestCase):
	
	def setUp(self):
		self.model = UnreadModel()

	def test_unread(self):
		self.model.collection.remove()
		unread = self.model.get_unread_values()
		
		eq_(1,unread['id'])

		# Check if there is a log and exception field
		eq_(True, unread.has_key('logs'))
		eq_(True, unread.has_key('exceptions'))

	
	def test_mark_logs_as_read(self):
		self.model.get_unread_values() # It will create the record if it doesn't exist
		self.model.collection.update({"id": 1}, {"$inc": {"logs": 1}})

		self.model.mark_logs_as_read()
		
		result = self.model.get_unread_values()
		eq_(result['logs'], 0)

	def test_mark_exceptions_as_read(self):
		self.model.get_unread_values() # It will create the record if it doesn't exist
		self.model.collection.update({"id": 1}, {"$inc": {"exceptions": 1}})

		self.model.mark_exceptions_as_read()
		
		result = self.model.get_unread_values()
		eq_(result['exceptions'], 0)
		

class TestSystemModel(unittest.TestCase):


	def setUp(self):
		self.model = SystemModel()


	def test_get_system_data(self):
		active_checks = ['cpu']
		# Delete everything in the cpu collection
		cpu = self.model.mongo.get_collection('cpu')
		cpu.remove()
		

		empty_result = self.model.get_system_data(active_checks, minute_ago, now)
		
		eq_(len(empty_result), 1) # Should return only the cpu field {cpu: pymongoobject}

		# Nothing in the cpu field
		for cpu in empty_result['cpu']:
			eq_(cpu, False)

		cpu.insert({"system" : 1, "idle" : 98, "user" : 0, "time" : minute_ago})
		cpu.insert({"system" : 1, "idle" : 98, "user" : 0, "time" : two_minutes_ago})
		cpu.insert({"system" : 1, "idle" : 98, "user" : 0, "time" : now})

		result = self.model.get_system_data(active_checks, two_minutes_ago, now)
		eq_(result['cpu'].count(), 3)

		result = self.model.get_system_data(active_checks, minute_ago, now)
		eq_(result['cpu'].count(), 2)

		# Cleanup the collection
		cpu.remove()


class TestProcessModel(unittest.TestCase):

	def setUp(self):
		self.model = ProcessModel()

	def test_get_process_data(self):
		
		active_checks = ['cron']
		cron = self.model.mongo.get_collection('cron')
		cron.remove()
		
		cron.insert({"memory" : "10.8", "time" : two_minutes_ago, "cpu" : "0.0" })
		cron.insert({"memory" : "10.8", "time" : minute_ago, "cpu" : "0.0" })
		cron.insert({"memory" : "10.8", "time" : now, "cpu" : "0.0" })


		result = self.model.get_process_data(active_checks, two_minutes_ago, now)
		eq_(result['cron'].count(), 3)


		result = self.model.get_process_data(active_checks, minute_ago, now)
		eq_(result['cron'].count(), 2)

		cron.remove()

		
class TestLogModel(unittest.TestCase):
	
	def setUp(self):
		self.model = LogModel()
		self.logs = self.model.mongo.get_collection('logs')


	def test_get_logs(self):
		self.logs.remove()

		self.logs.insert({"level" : "info", "message" : "test"})
		self.logs.insert({"level" : "info", "message" : "test"})
		self.logs.insert({"level" : "info", "message" : "test"})
		
		result = self.model.get_logs()
		eq_(result.count(), 3)
		
		self.logs.remove()


	def test_filtered_logs(self):
		self.logs.remove()
		
		self.logs.insert({"level" : "info", "message" : "test", "_searchable": "test"})
		self.logs.insert({"level" : "warning", "message" : "test", "_searchable": "test_more"})
		self.logs.insert({"level" : "debug", "message" : "test", "_searchable": "another_thing"})

		result = self.model.filtered_logs(['info'], None)
		eq_(result.count(), 1)

		
		result = self.model.filtered_logs(['info','debug'], None)
		eq_(result.count(), 2)


		result = self.model.filtered_logs(['info','debug','warning'], None)
		eq_(result.count(), 3)


		result = self.model.filtered_logs(['info'], 'test')
		eq_(result.count(), 1)


		result = self.model.filtered_logs([], 'test')
		eq_(result.count(), 2)
		
		self.logs.remove()


class TestExceptionModel(unittest.TestCase):


	def setUp(self):
		self.model = ExceptionModel()


	def test_get_exceptions(self):
		self.model.collection.remove()
		self.model.collection.insert({"exception_class" : "test", "message": "test", "last_occurrence": two_minutes_ago})
		self.model.collection.insert({"exception_class" : "test", "message": "test", "last_occurrence": minute_ago})

		result = self.model.get_exceptions()
		eq_(result.count(), 2)
		
		eq_(result[0]['last_occurrence'], minute_ago)
		
		self.model.collection.remove()


class TestDashboardModel(unittest.TestCase):
	
	
	def setUp(self):
		self.model = DashboardModel()

	
	def test_get_last_process_check(self):
		active_checks = ['cron']

		cron = self.model.mongo.get_collection('cron')
		cron.remove()
		
		cron.insert({"memory" : "10.8", "time" : two_minutes_ago, "cpu" : "0.0" })
		cron.insert({"memory" : "10.8", "time" : minute_ago, "cpu" : "0.0" })
		cron.insert({"last" : 1})


		result = self.model.get_last_process_check(active_checks)
		eq_(result['cron']['time'], minute_ago)
		
		cron.remove()


	def test_get_last_system_check(self):
		active_checks = ['cpu']

		cpu = self.model.mongo.get_collection('cpu')
		cpu.remove()
		
		cpu.insert({"system" : "10", "time" : two_minutes_ago })
		cpu.insert({"system": "10", "time" : minute_ago })
		cpu.insert({"last" : 1})


		result = self.model.get_last_system_check(active_checks)
		eq_(result['cpu']['time'], minute_ago)


		cpu.remove()


class TestUserModel(unittest.TestCase):

	def setUp(self):
		self.model = UserModel()


	def test_create_user(self):
		self.model.collection.remove()
		self.model.create_user({'username': "test", 'password': '1234'})
		eq_(self.model.collection.count(),1)
	

	def test_check_user(self):
		self.model.collection.remove()
		user_dict = {"username": "test", "password": "1234"}
		self.model.create_user(user_dict)

		result = self.model.check_user({"username": "test", "password": "1234"})

		# username, pass, _id
		eq_(len(result), 3)

		result = self.model.check_user({"username": "noname","password": ""})

		eq_(result, {})


	def test_username_exists(self):
		self.model.collection.remove()
		
		result = self.model.username_exists("test")
		eq_(result, 0)
		
		self.model.create_user({'username': "test", 'password': '1234'})

		result = self.model.username_exists("test")
		eq_(result, 1)


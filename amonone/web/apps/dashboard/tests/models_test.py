import unittest
from amonone.web.apps.dashboard.models import DashboardModel
from time import time
from nose.tools import eq_

now = int(time())
minute_ago = (now-60)
two_minutes_ago = (now-120)

class TestDashboardModel(unittest.TestCase):


	def setUp(self):
		self.model = DashboardModel()


	def test_get_process_check(self):

		servers = self.model.mongo.get_collection('servers')
		servers.remove()
		servers.insert({"name" : "test", "key": "server_key_test"})
		server = servers.find_one()
	
		server_process_collection = self.model.mongo.get_server_processes_collection(server)
		server_process_collection.remove()

		server_process_collection.insert({"memory" : "10.8", "time" : two_minutes_ago, "cpu" : "0.0", "server_id": server['_id']})
		server_process_collection.insert({"memory" : "10.8", "time" : minute_ago, "cpu" : "0.0", "server_id": server['_id']})
		server_process_collection.insert({"last" : 1, "server_id": server['_id']})


		result = self.model.get_process_check(server, None)
		
		eq_(result['details']['time'], minute_ago)

		server_process_collection.remove()
		servers.remove()


	def test_get_system_check(self):


		servers = self.model.mongo.get_collection('servers')
		servers.remove()
		servers.insert({"name" : "test", "key": "server_key_test"})
		server = servers.find_one()

			
		server_system_collection = self.model.mongo.get_server_system_collection(server)
		server_system_collection.insert({"system" : "10", "time" : two_minutes_ago , "server_id": server['_id']})
		server_system_collection.insert({"system": "10", "time" : minute_ago , "server_id": server['_id']})
		server_system_collection.insert({"last" : 1, "server_id": server['_id']})

		result = self.model.get_system_check(server, None)
		eq_(result['time'], minute_ago)

		servers.remove()
		server_system_collection.remove()
import unittest
from nose.tools import eq_
from amon.web.apps.api.models import ApiModel

class ApiModelTest(unittest.TestCase):

	def setUp(self):
		self.model = ApiModel()
		self.servers_collection = self.model.mongo.get_collection('servers')


	def check_server_test(self):
		self.servers_collection.remove()
		self.servers_collection.insert({"name" : "test", "key": 'test_me'})

		result = self.model.check_server_key('test_me')
		eq_(result['key'], 'test_me')


	def update_watched_processes_test(self):
		self.servers_collection.remove()
		self.servers_collection.insert({"name" : "test", "key": 'test_me'})

		self.model.server_update_processes('test_me',['process1','process2'])

		result = self.servers_collection.find_one()
		eq_(result['processes'],['process1','process2'])

	def update_disk_volumes_test(self):
		self.servers_collection.remove()
		self.servers_collection.insert({"name" : "test", "key": 'test_me'})

		self.model.server_update_disk_volumes('test_me',{"sda1": "test", "sda2": "test", "last": 1, "time": "now"})

		result = self.servers_collection.find_one()
		eq_(result['volumes'],[u'sda2',u'sda1'])


	def update_network_interfaces_test(self):
		self.servers_collection.remove()
		self.servers_collection.insert({"name" : "test", "key": 'test_me'})

		self.model.server_update_network_interfaces('test_me',{"eth1": "test", "lo": "test", "last": 1, "time": "now"})

		result = self.servers_collection.find_one()
		eq_(result['network_interfaces'],[u'eth1'])



	def store_system_entries_test(self):
		self.servers_collection.remove()
		self.servers_collection.insert({"name" : "test", "key": 'server_key_test_me'})
		server = self.servers_collection.find_one()

		server_system_collection = self.model.mongo.get_server_system_collection(server)
		server_system_collection.remove()

		self.model.store_system_entries('server_key_test_me',{u'memory':
			{u'swaptotal': 563, u'memfree': 1015, u'memtotal': 2012, u'swapfree': 563, u'time': 1326974020},
			u'loadavg': {"test":1}, u'disk': {"test1": 1 }, u'network': {'eth1': "test", "eth6": "test"}})

		
		result = server_system_collection.count()
		eq_(result,1)
		server_system_collection.remove({'server_id': server['_id']})

		server_updated = self.servers_collection.find_one()
		eq_(server_updated['volumes'],[u'test1'])
		eq_(server_updated['network_interfaces'],[u'eth6',u'eth1'])


	def store_process_entries_test(self):
		self.servers_collection.remove()
		self.servers_collection.insert({"name" : "test", "key": 'server_key_test_me'})
		server = self.servers_collection.find_one()

		server_process_collection = self.model.mongo.get_server_processes_collection(server)
		server_process_collection.remove()

		self.model.store_process_entries('server_key_test_me',{u'process': {u'memory': u'40.0', u'cpu': u'11.90', u'time': 1327169023}})

		result = server_process_collection.count()


		eq_(result,1)
		server_process_collection.remove({'server_id': server['_id']})

		server_updated = self.servers_collection.find_one()
		eq_(server_updated['processes'],[u'process'])


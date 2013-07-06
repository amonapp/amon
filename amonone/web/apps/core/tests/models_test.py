import unittest
from nose.tools import eq_
from amonone.web.apps.core.models import (
	ServerModel
)


class ServerModelTest(unittest.TestCase):

	def setUp(self):
		self.model = ServerModel()
		self.collection = self.model.mongo.get_collection('servers')


	def get_servers_for_group_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test", "alert_group": 'test'})

		result = self.model.get_servers_for_group('test')
		eq_(result.count(), 1)

	def check_server_exists_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test"})

		result = self.model.server_exists('test')
		eq_(result, 1)


	def update_server_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test"})
		server = self.collection.find_one()

		self.model.update({"name": "test_updated", "default": 1 }, server['_id'])

		result = self.collection.find_one()
		eq_(result['name'],'test_updated')


	def add_server_test(self):
		self.collection.remove()

		self.model.add('test', 'note','')

		result = self.collection.find_one()
		eq_(result['name'],'test')
		if result['key']:
			assert True


	def get_server_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test"})
		server = self.collection.find_one()

		result = self.model.get_by_id(server['_id'])
		eq_(result['name'],'test')
		eq_(result['_id'],server['_id'])


	def get_server_by_key_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test", "key": "test_me"})
		server = self.collection.find_one()

		result = self.model.get_server_by_key('test_me')
		eq_(result['name'],'test')
		eq_(result['key'],'test_me')
		eq_(result['_id'],server['_id'])


	def delete_server_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test", "key": "test_me"})
		server = self.collection.find_one()

		self.model.delete(server['_id'])

		result = self.collection.count()
		eq_(result,0)

	def servers_dict_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test", "key": "test_me"})
		self.collection.insert({"name" : "test2", "key": "test_me2"})

		servers = self.collection.find()
		result = self.model.get_all_dict()
		for server in servers:
			key =  unicode(server['_id'])
			if key in result.keys():
				assert True

	def get_all_servers_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test", "key": "test_me"})
		self.collection.insert({"name" : "test1", "key": "test_me_again"})

		result = self.model.get_all()
		eq_(result.count(), 2)

		self.collection.remove()

	def get_filtered_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test", "key": "test_me"})
		self.collection.insert({"name" : "test1", "key": "test_me_again"})
		self.collection.insert({"name" : "test2", "key": "test_me_one_more_time"})

		result = self.model.get_filtered(filter='all')
		eq_(result.count(), 3)

		# Get app ids
		server_ids = []
		for i in self.collection.find():
			server_ids.append(str(i['_id']))

		result = self.model.get_filtered(filter=server_ids)
		eq_(result.count(), 3)

		result = self.model.get_filtered(filter=server_ids[0:2])
		eq_(result.count(), 2)

		for r in result.clone():
			assert str(r['_id']) in server_ids[0:2]
		
		self.collection.remove()




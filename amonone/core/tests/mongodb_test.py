import unittest
from nose.tools import eq_
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from amonone.core.mongodb import backend

class TestMongoBackend(unittest.TestCase):
	
	def test_get_database(self):
		db = backend.get_database()
		eq_(db, Database(MongoClient(u'127.0.0.1', 27017), u'amon_test'))

	def test_get_connection(self):
		connection = backend.get_connection()
		eq_(connection, MongoClient(u'127.0.0.1', 27017))


	def test_get_server_system_collection(self):
		valid_server_key = {"key": 'testserverkey'}
		collection = backend.get_server_system_collection(valid_server_key)

		eq_(collection,
			Collection(Database(MongoClient('127.0.0.1', 27017), u'amon_test'), u'testserverkey_system')
		)

	def test_get_server_process_collection(self):
		valid_server_key = {"key": 'testserverkey'}
		collection = backend.get_server_processes_collection(valid_server_key)

		eq_(collection,
			Collection(Database(MongoClient('127.0.0.1', 27017), u'amon_test'), u'testserverkey_processes')
		)


	def test_string_to_valid_collection_name(self):
		name = 'TEST123456'
		valid_name = backend.string_to_valid_collection_name(name)
		eq_(valid_name, 'test123456')


	def test_store_entry(self):
		db = backend.get_collection('logs')
		db.remove()
		
		db.insert({})

		total_entries = db.count()
		eq_(1, total_entries)

		db.insert({})
		total_entries = db.count()
		eq_(2, total_entries)


	def test_store_entries(self):
	  db = backend.get_collection('cpu')
	  db.remove()
	  
	  entries_list = {'cpu': {'time': 1313096288, 'idle': 93, 'wait': 0, 'user': 2, 'system': 5}}

	  backend.store_entries(entries_list)

	  total_entries = db.count()
	  eq_(1, total_entries)



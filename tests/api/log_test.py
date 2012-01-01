import os
os.environ['AMON_ENV'] = 'test' # Switches the database to amon_test.

from nose.tools import eq_
import unittest
from amon.api import log


class TestLoggingApi(unittest.TestCase):

	def test_log(self):
		log.model.collection.remove()
		log({"bar":"baz"})
		eq_(1, log.model.collection.count())

	def test_log_contents(self):
		log.model.collection.remove()
		log({"message":"test"})

		entry = log.model.collection.find_one()
		eq_(entry['message'], 'test')
	
	def test_log_dict(self):
		log.model.collection.remove()
		log({"message": {"dict_key": "value", "dict_key2": "value_2"}})

		entry = log.model.collection.find_one()
		eq_(entry['message'], {u'dict_key': u'value', u'dict_key2': u'value_2'})


	def test_log_searchable_dict(self):
		log.model.collection.remove()
		log({"message": {"dict_key": "value", "dict_key2": "value_2"}})
		
		entry = log.model.collection.find_one()
		eq_(entry['_searchable'], 'dict_key:dict_key2')


	def test_log_searchable_string(self):
		log.model.collection.remove()
		log({"message": "test_message"})
		
		entry = log.model.collection.find_one()
		eq_(entry['_searchable'], 'test_message')
	
	
	def test_log_searchable_list(self):
		log.model.collection.remove()
		log({"message": ['test', 'more']})
		
		entry = log.model.collection.find_one()
		eq_(entry['_searchable'], 'test:more')

	def test_log_list_integers(self):
		log.model.collection.remove()
		log({"message": [1,2,3,4]})
		
		eq_(1, log.model.collection.count())


	def test_log_tags(self):
		log.model.collection.remove()

		tags = ['warning', 'info', 'debug', 'critical', 'error']
		
		log({"message":"", "tags": "warning"})
		log({"message":"", "tags": "info"})
		log({"message":"", "tags": "debug"})
		log({"message":"", "tags": "critical"})
		log({"message":"", "tags": "error"})

		eq_(5, log.model.collection.count())

		entries = log.model.collection.find()
		for entry in entries:
			self.assertTrue(entry['tags'] in tags)


	def test_empty_tag(self):
		log.model.collection.remove()
		log({"message":"test"})
		
		eq_(1, log.model.collection.count())

		entry = log.model.collection.find_one()
		eq_(entry['tags'], None)

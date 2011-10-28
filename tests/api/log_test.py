from amon.backends.mongodb import backend
from nose.tools import eq_
import unittest
from amon.api import log

class TestLoggingApi(unittest.TestCase):

	def setUp(self):
		backend.database = 'amon_test'


	def test_log(self):
		db = backend.get_collection('logs')
		db.remove()
		log({"bar":"baz"})
		eq_(1, db.count())


	def test_log_contents(self):
		db = backend.get_collection('logs')
		db.remove()
		log({"message":"test"})

		entry = db.find_one()
		eq_(entry['message'], 'test')


	def test_log_levels(self):
		db = backend.get_collection('logs')
		db.remove()
		
		levels = ('warning', 'error', 'info', 'critical', 'debug')
		
		log({"message":"", "level": "warning"})
		log({"message":"", "level": "info"})
		log({"message":"", "level": "debug"})
		log({"message":"", "level": "critical"})
		log({"message":"", "level": "error"})

		eq_(5, db.count())

		entries = db.find()
		for entry in entries:
			self.assertTrue(entry['level'] in levels)


	def test_undefined_log_levels(self):
		db = backend.get_collection('logs')
		db.remove()

		
		log({"message":"", "level": "dummy_level"})
		log({"message":"", "level": "and_another_one"})
		log({"message":"", "level": "and_even_more"})


		entries = db.find()
		for entry in entries:
			eq_(entry['level'], 'notset')

	def test_unread_counter(self):
		unread = backend.get_collection('unread')
		unread.remove()
		
		log({"message":"", "level": "dummy_level"})
		
		eq_(unread.count(), 1)

		log({"message":"", "level": "dummy_level"})
		log({"message":"", "level": "dummy_level"})

		eq_(unread.count(), 1)

	def test_unread_counter_values(self):
		unread = backend.get_collection('unread')
		unread.remove()
		
		log({"message":"", "level": "dummy_level"})

		unread_dict = unread.find_one()
		eq_(unread_dict['logs'],1)


		log({"message":"", "level": "dummy_level"})
		log({"message":"", "level": "dummy_level"})
		log({"message":"", "level": "dummy_level"})
		log({"message":"", "level": "dummy_level"})


		unread_dict = unread.find_one()
		eq_(unread_dict['logs'],5)

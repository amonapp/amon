import unittest
from amon.api.models import (
	LogsAPIModel,
	ExceptionAPIModel,
	CommonAPIModel
)
from nose.tools import eq_
import os
os.environ['AMON_ENV'] = 'test' # Switches the database to amon_test.

class TestLogsAPIModel(unittest.TestCase):
	
	def setUp(self):
		self.model = LogsAPIModel()

	def test_save_log(self):
		self.model.collection.remove()
		self.model.save_log({"test": "test"})
		eq_(1, self.model.collection.count())


	def test_upsert_tag(self):
		self.model.tags.remove()
		self.model.upsert_tag('test')
		eq_(1, self.model.tags.count())

	def test_duplicate_tag(self):
		self.model.tags.remove()
		self.model.upsert_tag('test')
		self.model.upsert_tag('test')
		self.model.upsert_tag('test')
		self.model.upsert_tag('test')
		eq_(1, self.model.tags.count())



class TestCommonAPIModel(unittest.TestCase):


	def setUp(self):
		self.model = CommonAPIModel()

	def test_upsert_unread_logs(self):
		self.model.unread.remove()

		self.model.upsert_unread('logs')
		eq_(1, self.model.unread.count())

		entry = self.model.unread.find_one()
		eq_(1,entry['logs'])
		eq_(0,entry['exceptions'])


	def test_upsert_unread_exceptions(self):
		self.model.unread.remove()

		self.model.upsert_unread('exceptions')
		eq_(1, self.model.unread.count())

		entry = self.model.unread.find_one()
		eq_(1,entry['exceptions'])
		eq_(0,entry['logs'])



class TestExceptionsAPIModel(unittest.TestCase):
	
	def setUp(self):
		self.model = ExceptionAPIModel()

	def test_save_exception(self):
		self.model.collection.remove()
		self.model.save_exception({"test": "test"})
		eq_(1, self.model.collection.count())

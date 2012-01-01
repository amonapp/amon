from nose.tools import eq_
import unittest
from amon.api import exception
from hashlib import md5

class TestExceptionApi(unittest.TestCase):

	def test_exception(self):
		exception.model.collection.remove()
		exception({"bar":"baz"})
		eq_(1, exception.model.collection.count())


	def test_exception_contents(self):
		exception.model.collection.remove()
		exception({"exception_class":"test",\
					"url": "url_test",\
					"backtrace": "backtrace_test",\
					"message": "message_test",\
					"enviroment": "enviroment",\
					"data":"data"})

		entry = exception.model.collection.find_one()
		eq_(entry['exception_class'], 'test')
		eq_(entry['url'], 'url_test')
		eq_(entry['backtrace'], 'backtrace_test')
		eq_(entry['additional_data'][0]['message'], 'message_test')
		eq_(entry['additional_data'][0]['enviroment'], 'enviroment')
		eq_(entry['additional_data'][0]['data'], 'data')


	def test_exception_id(self):
		exception.model.collection.remove()

		exception({"exception_class":"test",\
					"url": "url_test",\
					"backtrace": "backtrace_test"})

		exception_string = "{0}{1}{2}".format('test', 'url_test', 'backtrace_test')
		exception_id = md5(exception_string).hexdigest()

		entry = exception.model.collection.find_one()
		eq_(entry['exception_id'], exception_id)


	def test_exception_grouping(self):
		exception.model.collection.remove()
		
		exception({"exception_class":"test",\
					"url": "url_test",\
					"backtrace": "backtrace_test",\
					"data":"data"})
		
		exception({"exception_class":"test",\
					"url": "url_test",\
					"backtrace": "backtrace_test",\
					"data":"more data"})

		eq_(1, exception.model.collection.count())

	def test_exception_occurences_counter(self):
		exception.model.collection.remove()
		
		exception({"exception_class":"test",\
					"url": "url_test",\
					"backtrace": "backtrace_test"})
		
		exc = exception.model.collection.find_one()
		eq_(1, exc['total_occurrences'])

		exception({"exception_class":"test",\
					"url": "url_test",\
					"backtrace": "backtrace_test"})
		
		exc = exception.model.collection.find_one()
		eq_(2, exc['total_occurrences'])

	def test_exception_additional_data(self):
		exception.model.collection.remove()

		exception({"exception_class":"test",\
					"url": "url_test",\
					"backtrace": "backtrace_test"})


		exc = exception.model.collection.find_one()
		additional_data = exc['additional_data'][0]
		eq_(1, len(additional_data)) # Only occurrence should be here

		valid_keys = ['occurrence']
		keys = additional_data.keys()
		
		for key in keys:
			assert key in valid_keys

	#def test_unread_counter(self):
		#unread = backend.get_collection('unread')
		#unread.remove()
		
		#exception({"exception_class":"test","url": "url_test", "backtrace": "backtrace_test"})
		
		#eq_(unread.count(), 1)

		#exception({"exception_class":"test","url": "url_test", "backtrace": "backtrace_test"})
		#exception({"exception_class":"test","url": "url_test", "backtrace": "backtrace_test"})

		#eq_(unread.count(), 1)

	#def test_unread_counter_values(self):
		#unread = backend.get_collection('unread')
		#unread.remove()
		
		#exception({"exception_class":"test","url": "url_test", "backtrace": "backtrace_test"})

		#unread_dict = unread.find_one()
		#eq_(unread_dict['exceptions'],1)

		#exception({"exception_class":"test","url": "url_test", "backtrace": "backtrace_test"})
		#exception({"exception_class":"test","url": "url_test", "backtrace": "backtrace_test"})
		#exception({"exception_class":"test","url": "url_test", "backtrace": "backtrace_test"})
		#exception({"exception_class":"test","url": "url_test", "backtrace": "backtrace_test"})

		#unread_dict = unread.find_one()
		#eq_(unread_dict['exceptions'],5)

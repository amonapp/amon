from time import time
from amon.backends.mongodb import backend
import json

"""
 Exception structure:
	exception class
	message
	url
	backtrace
	enviroment
	additional data

"""
class Exception(object):

	def __init__(self):
		self.exception = {}

	def __call__(self, *args, **kwargs):
		
		now = int(time())

		exception_dict = json.loads(args[0])
		exception_class = exception_dict.get('exception_class', '')
		message= exception_dict.get('message', '')
		url = exception_dict.get('url', '')
		backtrace = exception_dict.get('backtrace', '')
		enviroment = exception_dict.get('enviroment', '')
		data = exception_dict.get('data', '')

		entry = {'time': now,
				 'message': message,
				 'url': url,
				 'enviroment': enviroment,
				 'backtrace' : backtrace,
				 'data': data,
				 'exception_class': exception_class
				 }
		
		backend.store_entry(entry, 'exceptions')

from time import time
from amon.api.models import ExceptionAPIModel, CommonAPIModel
from hashlib import md5

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
		self.model = ExceptionAPIModel()
		self.common_model = CommonAPIModel()

	def __call__(self, *args, **kwargs):
		
		now = int(time())

		exception_dict = args[0]
		exception_class = exception_dict.get('exception_class', '')
		url = exception_dict.get('url', '')
		backtrace = exception_dict.get('backtrace', '')
		
		message= exception_dict.get('message', '')
		enviroment = exception_dict.get('enviroment', '')
		data = exception_dict.get('data', '')
		
		
		exception_string = "{0}{1}{2}".format(exception_class, url, backtrace)
		exception_id = md5(exception_string).hexdigest()
		
		additional_data = {'occurrence': now}

		if message: additional_data['message'] = message
		if enviroment: additional_data['enviroment'] = enviroment
		if data: additional_data['data'] = data

		exception_in_db = self.model.collection.find_one({"exception_id" : exception_id})

		if exception_in_db is not None:
			exception_in_db['last_occurrence'] = now
			exception_in_db['additional_data'].insert(0, additional_data)
			exception_in_db['total_occurrences']  = exception_in_db['total_occurrences']+1

			self.model.collection.update({'_id' : exception_in_db['_id']}, exception_in_db)
		else:
			entry = {'last_occurrence': now,
					 'exception_id': exception_id,
					 'exception_class': exception_class,
					 'url': url,
					 'backtrace' : backtrace,
					 }

			entry['additional_data'] = [additional_data]
			entry['total_occurrences'] = 1
			
			self.model.save_exception(entry)
			
		self.common_model.upsert_unread('exceptions')

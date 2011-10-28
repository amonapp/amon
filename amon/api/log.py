from time import time
from amon.backends.mongodb import backend

class Log(object):

	def __init__(self):
		self.levels = ('warning', 'error', 'info', 'critical', 'debug')

	def __call__(self, *args, **kwargs):

		log_dict = args[0]

		try:
			level = log_dict.get('level')
			if level not in self.levels:
				level = 'notset'
		except: 
			level = 'notset'
		
		message = log_dict.get('message', '')

		now = int(time())
		entry = {'time': now, 'message': message, 'level': level}
		
		backend.store_entry(entry, 'logs')


		# TODO - refactor it at some point, when expanding the API
		unread = backend.get_collection('unread')
		unread_counter = unread.find({"id": 1}).count()

		if unread_counter == 0:
			_counter = {'id':1, 'exceptions': 0, 'logs': 1}
			unread.save(_counter)
		else:
			unread.update({"id": 1}, {"$inc": {"logs": 1}})

from time import time
from amon.backends.mongodb import backend

class Log(object):

	def __init__(self):
		self.levels = ('warning', 'error', 'info', 'critical', 'debug')

	def __call__(self, *args, **kwargs):
		
		level = kwargs.get('level', 'notset')
		message = args[0] # TODO - add fallback or error

		now = int(time())
		entry = {'time': now, 'message': message, 'level': level}
		
		backend.store_entry(entry, 'logs')
		

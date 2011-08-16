from time import time
from amon.backends.mongodb import backend

class AmonLog(object):

	def __init__(self):
		self.levels = ('warning', 'error', 'info', 'critical', 'debug')

	def log(self, message, level):
		
		if level not in self.levels:
			level = 'notset'
		
		now = int(time())
		entry = {'time': now, 'message': message, 'level': level}
		
		backend.store_entry(entry)
		

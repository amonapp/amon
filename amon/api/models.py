from amon.backends.mongodb import MongoBackend
from os import getenv

class BaseModel(object):
	
	def __init__(self):
		self.mongo = MongoBackend()
		
		# Set in the test suite 
		#  os.environ['AMON_ENV'] = 'test'
		if getenv('AMON_ENV', None) == 'test':
			self.mongo.database = 'amon_test'

class CommonAPIModel(BaseModel):

	def __init__(self):
		super(CommonAPIModel, self).__init__()
		self.unread = self.mongo.get_collection('unread')

	def upsert_unread(self, type):
		valid_types = ['logs', 'exceptions']
		
		if type in valid_types:
			unread_counter = self.unread.find({"id": 1}).count()

			if unread_counter == 0:
				other_type = 'logs' if type == 'exceptions' else 'exceptions'
				_counter = {'id':1, other_type: 0, type: 1}
				self.unread.save(_counter)
			else:
				self.unread.update({"id": 1}, {"$inc": {type: 1}})

class LogsAPIModel(BaseModel):

	def __init__(self):
		super(LogsAPIModel, self).__init__()
		self.collection = self.mongo.get_collection('logs')
		self.tags = self.mongo.get_collection('tags')

	def upsert_tag(self, tag):
		check_tag = self.tags.find_one({"tag": tag})
		
		if check_tag is None:
			self.tags.insert({"tag": tag})

	def save_log(self, log):
		self.collection.insert(log)

class ExceptionAPIModel(BaseModel):

	def __init__(self):
		super(ExceptionAPIModel, self).__init__()
		self.collection = self.mongo.get_collection('exceptions')

	def save_exception(self, exception):
		self.collection.insert(exception)

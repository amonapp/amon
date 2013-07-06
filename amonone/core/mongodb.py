import os
import re 

try:
	import pymongo
except ImportError:
	pymongo = None

try:
	import bson
except ImportError:
	bson = None

from amonone.core.exceptions import ImproperlyConfigured
from amonone.core import settings

class MongoBackend():


	internal_collections = ['sessions','users',]

	database = 'amonone'

	try: 
		if os.environ['AMON_TEST_ENV'] == 'True':
			database = 'amonone_test' # For the test suite
	except: 
		pass
	

	def __init__(self):
		self.pymongo = pymongo
		self.url = settings.MONGO
		self._database = None
		self._connection = None

	def get_connection(self):
		"""Connect to the MongoDB server."""
		from pymongo import MongoClient

		if self._connection is None:
			self._connection = MongoClient(host=self.url, max_pool_size=10)

		return self._connection


	def get_database(self, database=None):
		""""Get or create database  """
		database = database if database !=None else self.database
		
		if self._database is None:
			conn = self.get_connection()
			db = conn[database]
			self._database = db
		
		return self._database


	def get_collection(self, collection):
		db = self.get_database()

		collection = db[collection]

		return collection



	def store_entry(self, data=None, collection=None):
		""" Stores a system entry  """

		collection = self.get_collection(collection)

		if collection:
			collection.save(data, safe=True)	

	def index(self, collection):
		collection = self.get_collection(collection)
		collection.ensure_index([('time', pymongo.DESCENDING)])


	def get_object_id(self,id):
		return bson.objectid.ObjectId(id)

	def string_to_valid_collection_name(self, string):
		return re.sub(r'[^\w]', '', str(string)).strip().lower()

backend = MongoBackend()

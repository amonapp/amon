try:
	import pymongo
except ImportError:
	pymongo = None

from amon.core.exceptions import ImproperlyConfigured


class MongoBackend():
	mongodb_host = "localhost"
	mongodb_port = 27017
	mongodb_user = None
	mongodb_password = None
	mongodb_database = "amon"
	mongodb_system_collection = "amon_system"
	mongodb_log_collection = "amon_log"

	def __init__(self):
		if not pymongo:
			raise ImproperlyConfigured(
					"You need to install the pymongo library to use the "
					"MongoDB backend.")


		self._database = None
		self._connection = None

	def _get_connection(self):
		"""Connect to the MongoDB server."""
		if self._connection is None:
			from pymongo.connection import Connection
			self._connection = Connection(self.mongodb_host,
					self.mongodb_port)
			return self._connection


	def _get_database(self):
		""""Get database from MongoDB connection. """
		if self._database is None:
			conn = self._get_connection()
			db = conn[self.mongodb_database]
			self._database = db

		return self._database	

	def _get_system_collection(self):
		db = self._get_database()
		system_collection = db[self.mongodb_system_collection]

		return system_collection

	def _get_log_colletion(self):
		db = self._get_database()
		log_collection = db[self.mongodb_log_collection]

		return log_collection


	def _store_system_entry(self, entry):
		""" Stores a system entry  """
		
		system_collection = self._get_system_collection()
		system_collection.save(entry, safe=True)	


	def _store_log_entry(self, entry):
		
		log_collection = self._get_log_collection()
		log_collection.save(entry, safe=True)	

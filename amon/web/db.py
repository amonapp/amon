try:
	import pymongo
except ImportError:
	pymongo = None

from amon.backends.mongodb import MongoBackend

storage = MongoBackend()



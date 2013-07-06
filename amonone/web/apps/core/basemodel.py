from amonone.core.mongodb import MongoBackend
from pymongo import DESCENDING, ASCENDING

class BaseModel(object):

	def __init__(self):
		self.mongo = MongoBackend()
		self.db = self.mongo.get_database()
		
		self.desc = DESCENDING
		self.asc = ASCENDING

		self.collection = None # Defined in the child models


	# CRUD Methods
	def insert(self, data):
		self.collection.insert(data)

	def update(self, data, id):
		try:
			object_id =  self.mongo.get_object_id(id)
		except:
			object_id = False

		if object_id:
			self.collection.update({"_id": object_id}, {"$set": data}, upsert=True)

	def get_one(self):
		return self.collection.find_one()

	def get_all(self):
		return self.collection.find()

	def get_by_id(self,id):
		try:
			object_id =  self.mongo.get_object_id(id)
		except:
			object_id = False

		if object_id:
			return self.collection.find_one({"_id": object_id})

	def delete(self, id):
		try:
			object_id =  self.mongo.get_object_id(id)
		except:
			object_id = False

		if object_id:
			self.collection.remove(object_id)
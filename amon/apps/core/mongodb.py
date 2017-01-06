try:
    import pymongo
except ImportError:
    pymongo = None

try:
    import bson
except ImportError:
    bson = None
import re


from django.conf import settings


class MongoBackend():

    def __init__(self):

        self.pymongo = pymongo
        self.url = settings.MONGO_URL
        self.parsed_uri = pymongo.uri_parser.parse_uri(settings.MONGO_URL)

        self.database = self.parsed_uri.get('database') # Get the database from URI, could be None
        
        if self.database == None:
            self.database = 'amon'

        if settings.TESTING:
            self.database = 'amontest'

        self._database = None
        self._connection = None

    def get_connection(self):
        """Connect to the MongoDB server."""
        from pymongo import MongoClient

        if self._connection is None:
            self._connection = MongoClient(host=self.url)

        return self._connection


    def get_database(self, database=None):
        """"Get or create database  """
        database = database if database !=None else self.database

        if self._database is None:
            conn = self.get_connection()
            db = conn[database]
            self._database = db
        
        return self._database


    def get_collection(self, collection, append=None, prefix=''):
        db = self.get_database()

        collection = db[collection]

        return collection
    

    def get_object_id(self,id):
        return bson.objectid.ObjectId(id)

    def string_to_valid_collection_name(self, string):
        return re.sub(r'[^\w]', '', str(string)).strip().lower()


backend = MongoBackend()

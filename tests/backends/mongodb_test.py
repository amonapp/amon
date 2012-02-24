from nose.tools import eq_
import inspect
import unittest
from pymongo import Connection
from pymongo.collection import Collection
from pymongo.database import Database
from amon.backends.mongodb import backend
from amon.core import settings

class TestMongoBackend(unittest.TestCase):
    
    def setUp(self):
        backend.database = 'amon_test'

    def test_get_collection(self):
        eq_(backend.get_collection('logs'), Collection(Database(Connection(u'127.0.0.1', 27017), u'amon_test'), u'logs'))
        eq_(backend.get_collection('exceptions'), Collection(Database(Connection(u'127.0.0.1', 27017), u'amon_test'), u'exceptions'))

    def test_get_false_collection(self):
        self.assertFalse(backend.get_collection('test_me'))
        self.assertFalse(backend.get_collection('test_me_again'))


    def test_system_colllection(self):
        for setting in settings.SYSTEM_CHECKS:
            collection = Collection(Database(Connection(u'127.0.0.1', 27017), u'amon_test'), u'amon_{0}'.format(setting))
            eq_(backend.get_collection(setting), collection)

    def test_process_collection(self):
        for setting in settings.PROCESS_CHECKS:
            collection = Collection(Database(Connection(u'127.0.0.1', 27017), u'amon_test'), u'amon_{0}'.format(setting))
            eq_(backend.get_collection(setting), collection)


    def test_store_entry(self):
        db = backend.get_collection('logs')
        db.remove()
        
        db.insert({})

        total_entries = db.count()
        eq_(1, total_entries)

        db.insert({})
        total_entries = db.count()
        eq_(2, total_entries)


    def test_store_entries(self):
      db = backend.get_collection('cpu')
      db.remove()
      
      entries_list = {'cpu': {'time': 1313096288, 'idle': 93, 'wait': 0, 'user': 2, 'system': 5}}

      backend.store_entries(entries_list)


      total_entries = db.count()
      eq_(1, total_entries)



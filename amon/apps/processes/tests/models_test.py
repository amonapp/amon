import unittest
from nose.tools import * 
from time import time
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.servers.models import server_model
from amon.apps.processes.models import process_model


now = int(time())
minute_ago = (now-60)
two_minutes_ago = (now-120)
five_minutes_ago = (now-300)


class ProcessesModelTest(unittest.TestCase):

    def setUp(self):
        User.objects.all().delete()

        
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        

        self.account_id = 1

        server_model.collection.remove()

        server_key = server_model.add('test', account_id=self.account_id)
        
        self.server = server_model.get_server_by_key(server_key)
        self.server_id = self.server['_id']


    def tearDown(self):
        self.user.delete()
    
        
        process_model.collection.remove()
        server_model.collection.remove()


    def _cleanup(self):
        process_model.collection.remove()

        data_collection = process_model.mongo.get_collection("process_data")
        data_collection.remove()

        ignored = process_model.mongo.get_collection('ignored_processes')
        ignored.remove()



    def get_or_create_test(self):
        self._cleanup()
    
        process_model.get_or_create(server_id=self.server_id, name='test')

        
        total_devices = process_model.collection.find().count()
        eq_(total_devices, 1)

        process = process_model.get_or_create(server_id=self.server_id, name='test')
        
        eq_(process['name'], 'test')
        eq_(process['server'], self.server_id)

        
        total_devices = process_model.collection.find().count()
        eq_(total_devices, 1)
        

        self._cleanup()

        
    def save_data_test(self):
        self._cleanup()
            
        # It doesnt save process data when memory+cpu is below 2mb
        process_data = {
            u'nginx': {u'memory_mb': u'9.75', u'cpu': u'0.01', u'kb_read': u'0.01', u'kb_write': u'1.01'},
            u'apache': {u'memory_mb': u'0.78', u'cpu': u'3.00', u'kb_read': u'0.01', u'kb_write': u'1.01'},
            u'colord': {u'memory_mb': u'11.3', u'cpu': u'0.00', u'kb_read': u'0.01', u'kb_write': u'1.01'}, 
            u'acpid': {u'memory_mb': u'0.78', u'cpu': u'0.00' , u'kb_read': u'0.01', u'kb_write': u'1.01'}
        }

        expires_at = datetime.utcnow()+timedelta(hours=24)

        process_model.save_data(server=self.server, data=process_data, time=1, expires_at=expires_at)

        data_collection = process_model.mongo.get_collection("process_data")


        for r in data_collection.find():
            eq_(r['total_processes'], 4)
            eq_(r['t'], 1)
            eq_(len(r['data']), 2)
            eq_(r['expires_at'].date(), expires_at.date())


        # Last check update 
        process_collection = process_model.mongo.get_collection("processes")

        for r in process_collection.find():
            eq_(r['last_check'], 1)
        
                
        ignored_collection = process_model.mongo.get_collection('ignored_processes')
        for r in ignored_collection.find():
            eq_(r['t'], 1)
            eq_(r['data'], [u'acpid::0.0::0.78', u'colord::0.0::11.3'])
        
        self._cleanup()

        result = ignored_collection.find().count()

        # Test ingored processes cleanup
        for i in range(1, 10):
            process_model.save_data(server=self.server, data=process_data, time=i)

        ignored_collection = process_model.mongo.get_collection('ignored_processes')
        result = ignored_collection.find()

        eq_(result.clone().count() , 1)

        for r in result:
            eq_(r['t'], 9)
            eq_(r['server_id'], self.server['_id'])
        
        self._cleanup()

        for i in range(0, 10):
            process_model.save_data(server=self.server, data=process_data, time=1)

        for r in data_collection.find():

            eq_(r['total_processes'], 4)
            assert r['t'] <= 10
            eq_(len(r['data']), 2)

        self._cleanup()

        # Test top 3 Memory / CPU
        self._cleanup()

        process_data = {
            u'nginx': {u'memory_mb': u'9.75', u'cpu': u'0.01', u'kb_read': u'0.01', u'kb_write': u'1.01'},
            u'apache': {u'memory_mb': u'0.78', u'cpu': u'15.00', u'kb_read': u'0.01', u'kb_write': u'1.01'},
        }

        expires_at = datetime.utcnow()+timedelta(hours=24)

        process_model.save_data(server=self.server, data=process_data, time=1, expires_at=expires_at)

        data_collection = process_model.mongo.get_collection("process_data")


        for r in data_collection.find():
            eq_(r['total_processes'], 2)
            eq_(r['t'], 1)
            eq_(len(r['data']), 2)
            eq_(r['expires_at'].date(), expires_at.date())
            assert r['top_memory']
            assert r['top_memory'][0]['m'] == 9.75

            assert r['top_cpu']
            assert r['top_cpu'][0]['c'] == 15.00



    def is_ignored_test(self):
        self.assertFalse(process_model.is_ignored('test'))
        self.assertFalse(process_model.is_ignored('nginx'))

        self.assertTrue(process_model.is_ignored('ssh'))
        self.assertTrue(process_model.is_ignored('su'))
        

    def whitelist_process_test(self):
        self.assertTrue(process_model.whitelist_process('nginx'))
        self.assertTrue(process_model.whitelist_process('mysql'))
        


    def get_process_check_test(self):
        self._cleanup()

        data_collection = process_model.mongo.get_collection("process_data")


        for i in range(1, 10):
            process_data = {
                u'nginx': {u'memory_mb': u'9.75', u'kb_read': u'0.00', u'cpu': u'0.01', u'kb_write': u'0.00'},
                u'apache': {u'memory_mb': u'0.78', u'kb_read': u'-1.00', u'cpu': u'3.00', u'kb_write': u'-1.00'},
                u'colord': {u'memory_mb': u'11.3', u'kb_read': u'-1.00', u'cpu': u'0.00', u'kb_write': u'-1.00'}, 
                u'acpid': {u'memory_mb': u'0.78', u'kb_read': u'-1.00', u'cpu': u'0.00', u'kb_write': u'-1.00'}
            }

            process_model.save_data(server=self.server, data=process_data, time=i)


        # Last check update 
        process_collection = process_model.mongo.get_collection("processes")

        for r in process_collection.find():
            eq_(r['last_check'], 9)
        
        result = process_model.get_process_check(self.server, 9)

        for r in result:
            name = r.get('name')
            if name == 'apache':
                assert r['memory'] == 0.78
                assert r['cpu'] == 3.00
    
        
        self._cleanup()


    def get_ignored_test(self):
        self._cleanup()

        for i in range(1, 10):
            process_data = {
                u'colord': {u'memory_mb': u'11.3', u'kb_read': u'-1.00', u'cpu': u'25.00', u'kb_write': u'-1.00'}, 
                u'acpid': {u'memory_mb': u'0.78', u'kb_read': u'-1.00', u'cpu': u'0.00', u'kb_write': u'-1.00'}
            }

            process_model.save_data(server=self.server, data=process_data, time=i)


        result =  process_model.get_ignored_process_check(self.server, 9)
        for r in result:
            name = r.get('name')
            if name == 'colord':
                assert float(r['memory']) == 11.3
                assert float(r['cpu']) == 25.00
    
        self._cleanup()
    

    def get_all_for_server_test(self):
        self._cleanup()

        for i in range(0, 10):
            process_model.insert({'name': i, 'server': self.server['_id']})
        
        result = process_model.get_all_for_server(self.server['_id'])

        eq_(result.count(), 10)


    def get_data_for_period_test(self):
        self._cleanup()

        collection = process_model.mongo.get_collection("process_data")
        for i in range(0, 100):
            collection.insert({'name': i, 'server_id': self.server['_id'], 't': i})
        

        result = process_model._get_data_for_period_query(0, 10, self.server)

        eq_(result.clone().count(), 11) # gte 0, lte 10

        for i in result.clone():
            assert i['t'] <= 10
            assert i['t'] >= 0
        

    def get_memory_data_test(self):
        self._cleanup()
        

        process_model.insert({'name': 'test', 'server': self.server['_id']})
        process = process_model.collection.find_one()

        collection = process_model.mongo.get_collection("process_data")
        for i in range(0, 100):
            collection.insert({'server_id': self.server['_id'], 't': i, 'data': [{'p': process['_id'], 'm': 100, 'c': i}]})
        

        result = process_model.get_data_after(timestamp=10, enddate=20, server=self.server, process=process, check='memory')

        chart_data = result[0]['data']
        
        eq_(len(chart_data), 11)

        for entry in chart_data:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 100
        
        
    def get_cpu_data_test(self):
        self._cleanup()
        

        process_model.insert({'name': 'test', 'server': self.server['_id']})
        process = process_model.collection.find_one()

        collection = process_model.mongo.get_collection("process_data")
        for i in range(0, 100):
            collection.insert({'server_id': self.server['_id'], 't': i, 'data': [{'p': process['_id'], 'm': i, 'c': 99}]})
        

        result = process_model.get_data_after(timestamp=10, enddate=20, server=self.server, process=process, check='cpu')

        chart_data = result[0]['data']
        
        eq_(len(chart_data), 11)

        for entry in chart_data:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 99


    def get_top_consumers_for_period_test(self):
        self._cleanup()
        

        process_model.insert({'name': 'test', 'server': self.server['_id']})
        process = process_model.collection.find_one()

        collection = process_model.mongo.get_collection("process_data")
        for i in range(0, 100):
            collection.insert({'server_id': self.server['_id'], 't': i, 'data': [{'p': process['_id'], 'm': i, 'c': 99}]})
        

        result = process_model.get_top_consumers_for_period(date_from=10, date_to=20, server=self.server, metric_type='cpu')

        for r in result:
            eq_(r['name'], 'test')
            eq_(r['c'], 99)



    def get_first_check_date_test(self):
        self._cleanup()


        process_model.insert({'name': 'test', 'server': self.server['_id']})
        process = process_model.collection.find_one()

        collection = process_model.mongo.get_collection("process_data")
        for i in range(11, 100):
            collection.insert({'server_id': self.server['_id'], 't': i, 'data': [{'p': process['_id'], 'm': i, 'c': 99}]})
        

        result = process_model.get_first_check_date( server=self.server)

        eq_(result, 11)


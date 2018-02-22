import unittest
from time import time

from nose.tools import eq_

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.system.models import system_model
from amon.apps.servers.models import server_model
from amon.apps.devices.models import interfaces_model, volumes_model
from datetime import datetime, timedelta

now = int(time())
minute_ago = (now-60)
two_minutes_ago = (now-120)
five_minutes_ago = (now-300)


class SystemModelTest(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        
        self.account_id = 1

        server_model.collection.remove()
        server_key = server_model.add('testserver', account_id=self.account_id)
        
        self.server = server_model.get_server_by_key(server_key)
        self.server_id = self.server['_id']


    def tearDown(self):
        self.user.delete()
        User.objects.all().delete()
        
        interfaces_model.collection.remove()
        volumes_model.collection.remove()
        server_model.collection.remove()

    def _cleanup(self):
        data_collection = system_model.data_collection
        data_collection.remove()

        network_collection = interfaces_model.get_data_collection(server_id=self.server['_id'])
        network_collection.remove()

        disk_collection = volumes_model.get_data_collection(server_id=self.server['_id'])
        disk_collection.remove()


    def generate_charts_cpu_test(self):
        self._cleanup()


        collection = system_model.data_collection
        for i in range(10, 30):
            cpu_dict = {"time": i, "cpu" : { "iowait" : "0.00", "system" : "7.51", "idle" : "91.15", "user" : "1.34", "steal" : "0.00", "nice" : "0.00" }}
            collection.insert(cpu_dict)
        
        keys = [
                system_model.metric_tuple('idle', 'Idle'),
                system_model.metric_tuple('system', 'System'), 
                system_model.metric_tuple('user', 'User'),
                system_model.metric_tuple('iowait', 'IOWait'),
                system_model.metric_tuple('steal', 'Steal'),
                
            ]


        result = collection.find({"time": {"$gte": int(10), "$lte": int(20) }}).sort('time', system_model.asc)
    
        charts  = system_model.generate_charts(check='cpu', keys=keys, result=result)
            
        eq_(len(charts), 5)

        data = charts[0]['data']
        eq_(len(data), 11)

        for entry in data:
            assert entry['x'] >= 10
            assert entry['x'] <= 20


        self._cleanup()


    def get_data_collection_test(self):
        result = system_model.data_collection

        eq_(result.name, "system_data")


    def get_network_data_test(self):
        self._cleanup()

        interface = interfaces_model.get_or_create(server_id=self.server['_id'], name='test_interface')


        collection = interfaces_model.get_data_collection()
        for i in range(0, 30):
            collection.insert({'server_id': self.server_id,
                'device_id': interface['_id'], 't': i, 'i': 1, 'o': 2})
        

        result = system_model.get_device_data_after(timestamp=10, enddate=20, server=self.server, check='network', device_id=interface['_id'])

        inbound = result[0]['data']

        
        eq_(len(inbound), 11)

        for entry in inbound:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 1
            assert type(entry['y']) is float

        outbound = result[1]['data']
        
        eq_(len(outbound), 11)

        for entry in outbound:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 2


        # Test global data  - used in the dashboards
        all_servers = server_model.get_all()
        result = system_model.get_global_device_data_after(timestamp=10, enddate=20, filtered_servers=all_servers, check='network', key='i')

        used_percent = result[0]['data']
        
        eq_(len(used_percent), 11)
        assert result[0]['name'] == "{0}.test_interface".format(self.server['name'])

        for entry in used_percent:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 1.0
            assert type(entry['y']) is float

        self._cleanup()
        

    def get_disk_data_test(self):
        self._cleanup()
        
        volume = volumes_model.get_or_create(server_id=self.server['_id'], name='test_volume')
        collection = volumes_model.get_data_collection()

        for i in range(0, 30):
            collection.insert({
                'server_id': self.server_id,
                'device_id': volume['_id'], 't': i, 'total': 12, 'used': 2, 'percent': 60.0})
        

        result = system_model.get_device_data_after(timestamp=10, enddate=20, server=self.server, check='disk', device_id=volume['_id'])
        total = result[1]['data']

        
        eq_(len(total), 11)

        for entry in total:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 12
            assert type(entry['y']) is float


        used = result[0]['data']
        
        eq_(len(used), 11)

        for entry in used:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 2


        # Test global data  - used in the dashboards
        all_servers = server_model.get_all()
        result = system_model.get_global_device_data_after(timestamp=10, enddate=20, filtered_servers=all_servers, check='disk', key='percent')

        used_percent = result[0]['data']
        
        eq_(len(used_percent), 11)
        assert result[0]['name'] == "{0}.test_volume".format(self.server['name'])


        for entry in used_percent:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 60.0
            assert type(entry['y']) is float



        self._cleanup()


    def get_cpu_data_test(self):
        self._cleanup()

        collection = system_model.data_collection
        for i in range(0, 30):
            cpu_dict = {"time": i, 
                "server_id": self.server_id,
                "cpu" : { "iowait" : "0.00", "system" : "7.51", "idle" : "91.15", "user" : "1.34", "steal" : "0.00", "nice" : "0.00" }}
            collection.insert(cpu_dict)
        
        result = system_model.get_data_after(timestamp=10, enddate=20, server=self.server, check='cpu')

        t = ['idle', 'system', 'user', 'iowait' ,'steal']
        for i in range(0, 5):
            data_dict = result[i]['data']

            key = t[i]
            eq_(len(data_dict), 11)

            for entry in data_dict:
                assert entry['x'] >= 10
                assert entry['x'] <= 20

                assert entry['y'] == float(cpu_dict['cpu'][key])
                assert type(entry['y']) is float


        keys = [
                system_model.metric_tuple('idle', 'Idle'),
                system_model.metric_tuple('system', 'System'), 
                system_model.metric_tuple('user', 'User'),
                system_model.metric_tuple('iowait', 'IOWait'),
                system_model.metric_tuple('steal', 'Steal'),                
            ]

        result = collection.find({'server_id': self.server_id, 
                "time": {"$gte": int(10), "$lte": int(20) }}).sort('time', system_model.asc)
    
        charts  = system_model.generate_charts(check='cpu', keys=keys, result=result)
            
        eq_(len(charts), 5)

        data = charts[0]['data']
        eq_(len(data), 11)

        for entry in data:
            assert entry['x'] >= 10
            assert entry['x'] <= 20


        # Test global data  - used in the dashboards
        all_servers = server_model.get_all()
        result = system_model.get_global_data_after(timestamp=10, enddate=20, filtered_servers=all_servers, check='cpu', key='system')

        used_percent = result[0]['data']
        
        eq_(len(used_percent), 11)
        assert result[0]['name'] == self.server['name']


        for entry in used_percent:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 7.51
            assert type(entry['y']) is float


        self._cleanup()



    def get_memory_data_test(self):
        self._cleanup()

        collection = system_model.data_collection
        for i in range(0, 30):
            memory_dict = {"time": i,
            "server_id": self.server_id,
            "memory": {"used_percent": 15, "swap_used_mb": 0, "total_mb": 166, "free_mb": 4.44, "used_mb": 66.55,}}
            collection.insert(memory_dict)
        
        result = system_model.get_data_after(timestamp=10, enddate=20, server=self.server, check='memory')

        total = result[1]['data']
        
        eq_(len(total), 11)

        for entry in total:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 166
            assert type(entry['y']) is float


        used = result[0]['data']
        
        eq_(len(used), 11)

        for entry in used:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 66.55
            assert type(entry['y']) is float


        keys = [
                system_model.metric_tuple('total_mb', 'Total memory'), 
                system_model.metric_tuple('used_mb', 'Used memory'),         
            ]

        result = collection.find({'server_id': self.server_id, "time": {"$gte": int(10), "$lte": int(20) }}).sort('time', system_model.asc)
    
        charts  = system_model.generate_charts(check='memory', keys=keys, result=result)
            
        eq_(len(charts), 2)

        data = charts[0]['data']
        eq_(len(data), 11)

        for entry in data:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

        all_servers = server_model.get_all()

        # Test global data for memory - used in the dashboards
        result = system_model.get_global_data_after(timestamp=10, enddate=20, filtered_servers=all_servers, check='memory')

        used_percent = result[0]['data']
        
        eq_(len(used_percent), 11)
        assert result[0]['name'] == self.server['name']


        for entry in used_percent:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 15.0
            assert type(entry['y']) is float

        self._cleanup()



    def get_loadavg_data_test(self):
        self._cleanup()

        collection = system_model.data_collection
        for i in range(0, 30):
            data_dict = {"time": i,
            "server_id": self.server_id,
            "loadavg" : { "cores" : 4, "fifteen_minutes" : "0.18", "minute" : "0.34", "five_minutes" : "0.27" }}
            collection.insert(data_dict)
        
        result = system_model.get_data_after(timestamp=10, enddate=20, server=self.server, check='loadavg')


        t = ['minute', 'five_minutes', 'fifteen_minutes']
        for i in range(0, 3):
            result_dict = result[i]['data']

            key = t[i]
            eq_(len(result_dict), 11)

            for entry in result_dict:
                assert entry['x'] >= 10
                assert entry['x'] <= 20

                assert entry['y'] == float(data_dict['loadavg'][key])
                assert type(entry['y']) is float



        keys = [
                system_model.metric_tuple('minute', '1 minute'), 
                system_model.metric_tuple('five_minutes', '5 minutes'), 
                system_model.metric_tuple('fifteen_minutes', '15 minutes'), 
            ]

        result = collection.find({'server_id': self.server_id, "time": {"$gte": int(10), "$lte": int(20) }}).sort('time', system_model.asc)
    
        charts  = system_model.generate_charts(check='loadavg', keys=keys, result=result)
            
        eq_(len(charts), 3)

        data = charts[0]['data']
        eq_(len(data), 11)

        for entry in data:
            assert entry['x'] >= 10
            assert entry['x'] <= 20


        # Test global data  - used in the dashboards
        all_servers = server_model.get_all()
        result = system_model.get_global_data_after(timestamp=10, enddate=20, filtered_servers=all_servers, check='loadavg', key='minute')

        used_percent = result[0]['data']
        
        eq_(len(used_percent), 11)
        assert result[0]['name'] == self.server['name']


        for entry in used_percent:
            assert entry['x'] >= 10
            assert entry['x'] <= 20

            assert entry['y'] == 0.34
            assert type(entry['y']) is float


        self._cleanup()
            

    def get_first_check_date_test(self):
        self._cleanup()

        collection = system_model.data_collection

        for i in range(11, 100):
            collection.insert({'time': i, 'server_id': self.server['_id']})
        

        result = system_model.get_first_check_date(server=self.server)

        eq_(result, 11)



    def save_data_test(self):
        self._cleanup()


        expires_at = datetime.utcnow()+timedelta(hours=24)


        last_check = 99999
        system_data = {u'disk': 
            {u'sda1': 
            {u'used': u'21350', u'percent': u'46', u'free': u'25237', u'volume': u'/dev/sda1', u'path': u'/', u'total': u'49086'}}, 
        u'memory': 
            {u'used_percent': 34, u'swap_used_mb': 0, u'total_mb': 3954, u'free_mb': 2571, u'swap_used_percent': 0,
             u'swap_free_mb': 0, u'used_mb': 1383, u'swap_total_mb': 0}, 
        u'loadavg': {u'cores': 4, u'fifteen_minutes': u'0.36', u'minute': u'0.12', u'five_minutes': u'0.31'}, 
        u'network': {u'eth3': {u'inbound': u'6.05', u'outbound': u'1.97'}}, 
        u'cpu': {u'iowait': u'0.00', u'system': u'1.32', u'idle': u'98.68', u'user': u'0.00', u'steal': u'0.00', u'nice': u'0.00'}}

        system_model.save_data(self.server, system_data, time=last_check, expires_at=expires_at)

        

        disk_collection = volumes_model.get_data_collection(server_id=self.server['_id'])
        disk = volumes_model.get_by_name(server=self.server, name='sda1')

        eq_(disk_collection.find().count(), 1)

        for r in disk_collection.find():
            eq_(r['t'], last_check)
            eq_(r['total'], "49086")
            eq_(r['used'], "21350")
            eq_(r['device_id'], disk['_id'])
            eq_(r['expires_at'].date(), expires_at.date())
        


        network_collection = interfaces_model.get_data_collection(server_id=self.server['_id'])
        adapter = interfaces_model.get_by_name(server=self.server, name='eth3')

        eq_(network_collection.find().count(), 1)

        for r in network_collection.find():
            eq_(r['t'], last_check)
            eq_(r['i'], "6.05")
            eq_(r['o'], "1.97")
            eq_(r['device_id'], adapter['_id'])
            eq_(r['expires_at'].date(), expires_at.date())


        data_collection = system_model.data_collection
        for r in data_collection.find():
            eq_(r['time'], last_check)
            eq_(r['memory']['free_mb'], 2571)
            eq_(r['loadavg']['fifteen_minutes'], '0.36')
            eq_(r['cpu']['system'], '1.32')
            eq_(r['expires_at'].date(), expires_at.date())
            
        server_updated = server_model.get_by_id(self.server['_id'])

        eq_(server_updated['last_check'], last_check)


        self._cleanup()



    def get_last_check_test(self):
        self._cleanup()
        collection = system_model.data_collection


        for i in range(11, 100):
            collection.insert({'server_id': self.server['_id'], 'time': i })
        

        result = system_model.get_first_check_date(server=self.server)

        eq_(result, 11)

        self._cleanup()



    # def get_global_device_data_after_test(self):
    #     assert False


    # def get_global_data_after_test(self):
    #     assert False


    # def get_device_data_after(self):
    #     assert False
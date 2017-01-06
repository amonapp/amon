import json

from django.test.client import Client
from django.test import TestCase
from django.core.urlresolvers import reverse
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()

from amon.apps.servers.models import server_model, interfaces_model, volumes_model
from amon.apps.system.models import system_model


class TestSystemViews(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        

        self.account_id = 1

        self.c.login(username='foo@test.com', password='qwerty')


        server_model.add('testserver', account_id=self.account_id)
        self.server = server_model.collection.find_one()

        url = reverse('ajax_get_data_after')
        self.base_ajax_url = "{0}?server_id={1}".format(url, self.server['_id'])


    def tearDown(self):
        self.c.logout()
        self.user.delete()
        
        
        server_model.collection.remove()


    def server_system_test(self):
        url = reverse('server_system', kwargs={'server_id': self.server['_id']})    
        response = self.c.get(url)

        assert response.status_code == 200


    def ajax_get_data_no_enddate_test(self):
        url = "{0}?server_id={1}&check=cpu".format(
            reverse('ajax_get_data_after'), 
            self.server['_id']
        )


        response = self.c.get(url)

        assert response.status_code == 200

        url = "{0}?server_id={1}&check=network".format(
            reverse('ajax_get_data_after'), 
            self.server['_id']
        )

        response = self.c.get(url)

        assert response.status_code == 200


    def ajax_get_nodata_for_period_test(self):
        response = self.c.get(self.base_ajax_url)
        
        assert response.status_code == 200

        url = "{0}&check=cpu&timestamp=1".format(self.base_ajax_url)
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))
        data = to_json['data']
        
        eq_(len(data), 5)  # System, wait, idle, sleep, user

        url = "{0}&check=memory&timestamp=1".format(self.base_ajax_url)
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))
        data = to_json['data']

        eq_(len(data), 2)  # Total, Used


        url = "{0}&check=disk&device_id=1&timestamp=1".format(self.base_ajax_url)
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))
        data = to_json['data']

        eq_(len(data), 2)  # Total, Used


        url = "{0}&check=loadavg&timestamp=1".format(self.base_ajax_url)
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))
        data = to_json['data']

        eq_(len(data), 3)  # 1, 5, 15



    def ajax_get_memory_data_after_test(self):
        system_collection = system_model.data_collection
    
        memory_dict = {"time": 1,  
        "server_id": self.server['_id'],
        "memory": {"used_percent": 0, "swap_used_mb": 0, "total_mb": 100, "free_mb": 10, "used_mb": 10,}}
        system_collection.insert(memory_dict)

        url = "{0}&check=memory&timestamp=1".format(self.base_ajax_url)
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))

        assert to_json['now_local']
        assert to_json['last_update']

        data = to_json['data']

        total_memory_dict = data[1]


        eq_(total_memory_dict['data'], [{u'y': 100, u'x': 1}])
        
        used_memory_dict = data[0]
        eq_(used_memory_dict['data'], [{u'y': 10, u'x': 1}])    

        system_collection.remove()



    def ajax_get_loadavg_data_after_test(self):
        system_collection = system_model.data_collection
    
        memory_dict = {"time": 10, "server_id": self.server['_id'],
        "loadavg" : { "cores" : 4, "fifteen_minutes" : "0.18", "minute" : "0.34", "five_minutes" : "0.27" }}
        system_collection.insert(memory_dict)

        url = "{0}&check=loadavg&timestamp=1".format(self.base_ajax_url)
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))



        assert to_json['now_local']
        assert to_json['last_update']

        data = to_json['data']

        minute = data[0]

        eq_(minute['data'], [{u'y': 0.34, u'x': 10}])
        
        five_minutes = data[1]
        eq_(five_minutes['data'], [{u'y': 0.27, u'x': 10}])    


        fifteen_minutes = data[2]
        eq_(fifteen_minutes['data'], [{u'y': 0.18, u'x': 10}])    

        system_collection.remove()



    def ajax_get_cpu_data_after_test(self):
        system_collection = system_model.data_collection
    
        data_dict = {"time": 10,
        "server_id": self.server['_id'],
         "cpu" : { "iowait" : "0.00", "system" : "7.51", "idle" : "91.15", "user" : "1.34", "steal" : "0.00", "nice" : "0.00" }}
        system_collection.insert(data_dict)

        url = "{0}&check=cpu&timestamp=1".format(self.base_ajax_url)
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))


        assert to_json['now_local']
        assert to_json['last_update']
    
        data = to_json['data']
        idle = data[0]

        eq_(idle['data'], [{u'y': 91.15, u'x': 10}])
        
        system = data[1]
        eq_(system['data'], [{u'y': 7.51, u'x': 10}])    


        user = data[2]
        eq_(user['data'], [{u'y':1.34, u'x': 10}])    

        iowait = data[3]
        eq_(iowait['data'], [{u'y':0.00, u'x': 10}])

        steal = data[4]
        eq_(steal['data'], [{u'y':0.00, u'x': 10}])

        system_collection.remove()



    def ajax_get_network_data_after_test(self):
        network_collection = interfaces_model.get_data_collection()

        
        adapter = interfaces_model.get_or_create(server_id=self.server['_id'], name='test')
        adapter_dict = {"t": 10, "o" : 6.12, "i" : 1.11, "device_id": adapter['_id'], "server_id": self.server['_id'],}
        network_collection.insert(adapter_dict)

        url = "{0}&check=network.inbound&timestamp=1".format(self.base_ajax_url)
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))

        
        assert to_json['now_local']
        assert to_json['last_update']
    
        data = to_json['data']

        inbound = data[0]

        eq_(inbound['data'], [{u'y': 1.11, u'x': 10}])

        url = "{0}&check=network.outbound&timestamp=1".format(self.base_ajax_url)
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))

        assert to_json['now_local']
        assert to_json['last_update']
        data = to_json['data']

        outbound = data[0]
        eq_(outbound['data'], [{u'y': 6.12, u'x': 10}])
        

        interfaces_model.delete(adapter['_id'])
        network_collection.remove()



    def ajax_get_volume_data_after_test(self):
        disk_collection = volumes_model.get_data_collection()
        
        volume = volumes_model.get_or_create(server_id=self.server['_id'], name='test')
        disk_dict = {"t": 10, "used" : "19060", "percent" : "41", "free" : "27527", "total": 62, "device_id": volume['_id'], "server_id": self.server['_id']}
        disk_collection.insert(disk_dict)

        url = "{0}&check=disk&device_id={1}&timestamp=1".format(self.base_ajax_url, volume['_id'])
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))

        assert to_json['now_local']
        assert to_json['last_update']
    
        data = to_json['data']

    
        total = data[1]
        eq_(total['data'], [{u'y': 62, u'x': 10}])


        free = data[0]
        eq_(free['data'], [{u'y': 19060.0, u'x': 10}])
        

        volumes_model.delete(volume['_id'])
        disk_collection.remove()
import json
from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.servers.models import server_model
from amon.apps.processes.models import process_model


class TestProcessViews(TestCase):

    def setUp(self):
        User.objects.all().delete()
        
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        

        self.account_id = 1
        self.c.login(username='foo@test.com', password='qwerty')


        server_model.add('testserver', account_id=self.account_id)
        self.server = server_model.collection.find_one()
        self.server_id = self.server['_id']


        process_model.insert({'name': 'test', 'server': self.server['_id']})
        self.process = process_model.collection.find_one()


    def tearDown(self):
        self.c.logout()
        self.user.delete()
        

        server_model.collection.remove()
        process_model.collection.remove()


    def view_process_test(self):
        url = reverse('view_process', kwargs={'server_id': self.server['_id']})    
        url = "{0}?process={1}".format(url, self.process['_id'])

        response = self.c.get(url)

        assert response.status_code == 200



    def ajax_get_process_nodata_after_test(self):
        url = reverse('ajax_get_process_data_after')    
        url = "{0}?check=cpu&server_id={1}&timestamp=1".format(url, self.server['_id'])
        
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))

    
        series = to_json['data']

        assert to_json['last_update']
        assert to_json['now_local']


        eq_(len(series), 1)  # CPU

        url = "{0}?check=memory&server_id={1}&timestamp=1".format(url, self.server['_id'])
        
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))

        series = to_json['data']

        assert to_json['last_update']
        assert to_json['now_local']

    
        eq_(len(series), 1) # Memory


    def ajax_get_process_cpu_data_after_test(self):
        process_collection = process_model.mongo.get_collection("process_data")
        

        process_dict = {'server_id': self.server_id, 
            "t": 10, "data": [{"p": self.process['_id'] , "c": 0.01, "m": 1.56}]}
        process_collection.insert(process_dict)

        url = reverse('ajax_get_process_data_after')    
        url = "{0}?check=cpu&server_id={1}&timestamp=1&process={2}".format(url, self.server['_id'], self.process['_id'])
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))


        series = to_json['data']

        assert to_json['last_update']
        assert to_json['now_local']

        eq_(series[0]['data'], [{u'y': 0.01, u'x': 10}])
    

        process_collection.remove()

    def ajax_get_process_memory_data_after_test(self):
        process_collection = process_model.mongo.get_collection("process_data")
        

        process_dict = {'server_id': self.server_id,
            "t": 10, "data": [{"p": self.process['_id'] , "c": 0.01, "m": 1.56}]}
        process_collection.insert(process_dict)

        url = reverse('ajax_get_process_data_after')    
        url = "{0}?check=memory&server_id={1}&timestamp=1&process={2}".format(url, self.server['_id'], self.process['_id'])
    
        response = self.c.get(url)
        to_json = json.loads(response.content.decode('utf-8'))

        series = to_json['data']

        assert to_json['last_update']
        assert to_json['now_local']

        eq_(series[0]['data'], [{u'y': 1.56, u'x': 10}])


        process_collection.remove()


    def ajax_monitor_process_test(self):
        process_model.collection.remove()

        process_collection = process_model.mongo.get_collection("process_data")
        process_collection.remove()

    

        url = reverse('ajax_monitor_process')    
        url = "{0}?server_id={1}&name=compiz".format(url, self.server['_id'])
        response = self.c.get(url)

        to_json = json.loads(response.content.decode('utf-8'))

        eq_(to_json['Response'], 'OK')
        
        result = process_model.collection.find_one()


        eq_(result['name'], 'compiz')
        eq_(result['server'], self.server_id)

        
        process_model.collection.remove()
        process_collection.remove()
    



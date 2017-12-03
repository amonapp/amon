import json
from django.test.client import Client
from django.urls import reverse
from django.test import TestCase
from nose.tools import *

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.dashboards.models import dashboard_model, dashboard_metrics_model
from amon.apps.plugins.models import plugin_model


class TestDashboardAPI(TestCase):

    def setUp(self):
        User.objects.all().delete()
        
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        


        self.c.login(username='foo@test.com', password='qwerty')
        self.account_id = 1

        self.collection = dashboard_model.collection
        self.servers_collection = dashboard_model.mongo.get_collection('servers')

        self.servers_collection.insert({"name" : "testserver", 'account_id': self.account_id})
        self.server = self.servers_collection.find_one()
        self.server_id = self.server['_id']
        self.server_id_str = str(self.server['_id'])

        self.collection.insert({"name" : "testdashboard"})

        self.dashboard = self.collection.find_one()
        self.dashboard_id = self.dashboard['_id']


        self.process_collection = dashboard_metrics_model.mongo.get_collection('processes')
        self.process_collection.remove()

        self.process_collection.insert({"name" : "testprocess"})
        self.process = self.process_collection.find_one()
        self.process_id = self.process['_id']


        self.plugins_collection = dashboard_metrics_model.mongo.get_collection('plugins')
        self.plugins_collection.remove()

        self.plugins_collection.insert({"name" : "testplugin"})
        self.plugin = self.plugins_collection.find_one()
        self.plugin_id = self.plugin['_id']


        self.metrics_collection = dashboard_metrics_model.mongo.get_collection('metrics')
        
        self.metrics_collection.remove()
        self.metrics_collection.insert({"name" : "testmetric" , 'account_id': self.account_id, "type": 'gauge'})
        self.metric = self.metrics_collection.find_one()
        self.metric_id = self.metric['_id']

    def tearDown(self):
        self.servers_collection.remove()
        self.collection.remove()
        self.process_collection.remove()
        self.plugins_collection.remove()
        self.metrics_collection.remove()
        self.c.logout()
        self.user.delete()
        


    def _cleanup(self):
        self.collection.remove()
        dashboard_metrics_model.collection.remove()
        

    def test_add_metric(self):
        self._cleanup()

        
        url = reverse('ajax_dashboard_add_metric', kwargs={'dashboard_id': self.dashboard_id})

        # Check adding different metrics 

        # System metrics
        data = {"check": "cpu" , "server_id": "{0}".format(self.server_id_str), 
        "account_id": self.account_id }
        response =  self.c.post(url, data=json.dumps(data), content_type='application/json')

        
        assert response.status_code == 200
        
        json_string = response.content.decode('utf-8')
        result_data = json.loads(json_string)
        

        assert result_data['response'] == 'Created'

        result = dashboard_metrics_model.collection.find_one()
        
        assert result['server_id'] == self.server_id
        assert result['dashboard_id'] == self.dashboard_id
        assert result['check'] == 'cpu'


        # Process metrics
        dashboard_metrics_model.collection.remove()

        data = {"check": "memory" , 
            "server_id": "{0}".format(self.server_id_str), 
            "process_id": "{0}".format(str(self.process_id)), 
            "account_id": self.account_id 

        }
        

        response =  self.c.post(url, data=json.dumps(data), content_type='application/json')

        
        assert response.status_code == 200
        
        json_string = response.content.decode('utf-8')
        result_data = json.loads(json_string)
        

        assert result_data['response'] == 'Created'

        result = dashboard_metrics_model.collection.find_one()
        
        assert result['server_id'] == self.server_id
        assert result['process_id'] == self.process_id
        assert result['dashboard_id'] == self.dashboard_id
        assert result['check'] == 'memory'


        # Plugin metrics

        dashboard_metrics_model.collection.remove()

        plugin_model.gauge_collection.remove()
        gauge = plugin_model.get_or_create_gauge_by_name(plugin=self.plugin, name='count')

        data = {"check": "plugin" ,
            "gauge_id":  "{0}".format(str(gauge['_id'])),
            "server_id": "{0}".format(self.server_id_str), 
            "plugin_id": "{0}".format(str(self.plugin_id)), 
            "account_id": self.account_id 

        }
        

        response =  self.c.post(url, data=json.dumps(data), 
            content_type='application/json')

        
        assert response.status_code == 200
        
        json_string = response.content.decode('utf-8')
        result_data = json.loads(json_string)
        

        assert result_data['response'] == 'Created'

        result = dashboard_metrics_model.collection.find_one()
        
        assert result['server_id'] == self.server_id
        assert result['gauge_id'] == gauge['_id']
        assert result['plugin_id'] == self.plugin_id
        assert result['dashboard_id'] == self.dashboard_id
        assert result['check'] == 'plugin'

        
        self._cleanup()


    def test_remove_metric(self):

        dashboard_metrics_model.collection.remove()

        data = {"check": "metric" ,
            "metric_id":  "{0}".format(str(self.metric['_id'])),
            "account_id": self.account_id 

        }

        url = reverse('ajax_dashboard_add_metric', kwargs={'dashboard_id': self.dashboard_id})
        response =  self.c.post(url, data=json.dumps(data), content_type='application/json')

        assert dashboard_metrics_model.collection.find().count() == 1

        result = dashboard_metrics_model.collection.find_one()

        url = reverse('ajax_dashboard_remove_metric')
        data = {
            "metric_id":  "{0}".format(str(result['_id'])),
        }
        response =  self.c.post(url, data=json.dumps(data), content_type='application/json')
        
        assert response.status_code == 200
    
        assert dashboard_metrics_model.collection.find().count() == 0



    def test_get_all_metrics(self):
        self._cleanup()

        url = reverse('ajax_dashboard_add_metric', kwargs={'dashboard_id': self.dashboard_id})


        dashboard_metrics_model.collection.remove()

        data = {
            "check": "metric" ,
            "metric_type": "application",
            "metric_id":  "{0}".format(str(self.metric['_id'])),
            "account_id": self.account_id 

        }
        response =  self.c.post(url, data=json.dumps(data), 
            content_type='application/json')


        plugin_model.gauge_collection.remove()
        gauge = plugin_model.get_or_create_gauge_by_name(plugin=self.plugin, name='count')

        data = {"check": "plugin" ,
            "plugin_id": "{0}".format(str(self.plugin_id)), 
            "gauge_id":  "{0}".format(str(gauge['_id'])),
            "server_id": "{0}".format(self.server_id_str), 
            "account_id": self.account_id 

        }
        

        response =  self.c.post(url, data=json.dumps(data), 
            content_type='application/json')


        data = {"check": "memory" , 
            "server_id": "{0}".format(self.server_id_str), 
            "process_id": "{0}".format(str(self.process_id)), 
            "account_id": self.account_id 

        }
        
        response =  self.c.post(url, data=json.dumps(data),
         content_type='application/json')


        url = reverse('ajax_dashboard_get_all_metrics', 
            kwargs={'dashboard_id': self.dashboard_id})
        result = self.c.get(url)

        assert result.status_code == 200

        for r in result.data['data']:
            metric_type = r.get('metric_type')
            type = r.get('type')


            if metric_type == 'plugin':
                assert r['name'] == "{0}.{1}.{2}".format(self.server['name'], self.plugin['name'], gauge['name'])
                assert r['gauge_id'] == str(gauge['_id'])
                assert r['plugin_id'] == str(self.plugin['_id'])
                    
            elif metric_type == 'process':
                assert r['name'] == "{0}.{1}.{2}".format(self.server['name'], self.process['name'], 'memory')
                assert r['process_id'] == str(self.process['_id'])
                assert r['server_id'] == str(self.server['_id'])
            


        

    # def test_public_dashboard_metrics(self):
    #     assert False
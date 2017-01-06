import unittest
from nose.tools import * 

from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.dashboards.models import dashboard_model, dashboard_metrics_model
from amon.apps.plugins.models import plugin_model


class DashboardModelTest(unittest.TestCase):

    def setUp(self):
        User.objects.all().delete()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        
        self.account_id = 1
    

        self.collection = dashboard_model.collection
        self.servers_collection = dashboard_model.mongo.get_collection('servers')

        self.servers_collection.insert({"name" : "test"})
        self.server = self.servers_collection.find_one()
        self.server_id = self.server['_id']


    def tearDown(self):
        self.servers_collection.remove()
        self.collection.remove()
        User.objects.all().delete()
        


    def _cleanup(self):
        self.collection.remove()

    def get_all_test(self):
        self._cleanup()

        for i in range(5):
            self.collection.insert({'test': 1, 'server': i})
            

        result = dashboard_model.get_all()

        eq_(result, None)

        for i in range(5):
            self.collection.insert({'test': 1, 'account_id': i})


        result = dashboard_model.get_all(account_id=1)

        eq_(result.count(), 1)
        
        self._cleanup()





    def create_test(self):
        self._cleanup()
        
        result = dashboard_model.create({'test': 1})

        assert len(str(result)) == 24 # object_id


        self._cleanup()


class DashboardMetricsModelTest(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        

        self.account_id = 1
        

        self.collection = dashboard_metrics_model.collection

        self.servers_collection = dashboard_metrics_model.mongo.get_collection('servers')

        self.servers_collection.insert({"name" : "testserver"})
        self.server = self.servers_collection.find_one()
        self.server_id = self.server['_id']


        dashboard_model.collection.insert({"name" : "testdashboard"})
        self.dashboard = dashboard_model.collection.find_one()
        self.dashboard_id = self.dashboard['_id']


        self.process_collection = dashboard_metrics_model.mongo.get_collection('processes')

        self.process_collection.insert({"name" : "testprocess"})
        self.process = self.process_collection.find_one()
        self.process_id = self.process['_id']


        self.plugins_collection = dashboard_metrics_model.mongo.get_collection('plugins')

        self.plugins_collection.insert({"name" : "testplugin"})
        self.plugin = self.plugins_collection.find_one()
        self.plugin_id = self.plugin['_id']


        # Will populate the keys
        data = {'t': 1, 'count.count_key': 2, 'second.second_key': 4, 'more.more_key': 5 }
        plugin_model.save_gauges(plugin=self.plugin, data=data, time=1)


        self.metrics_collection = dashboard_metrics_model.mongo.get_collection('metrics')

        self.metrics_collection.insert({"name" : "testmetric", "type": "gauge"})
        self.metric = self.metrics_collection.find_one()
        self.metric_id = self.metric['_id']


    def tearDown(self):
        self.collection.remove()
        dashboard_model.collection.remove()
        self.servers_collection.remove()
        self.process_collection.remove()
        self.plugins_collection.remove()
        plugin_model.gauge_collection.remove()
        User.objects.all().delete()
        


    def _cleanup(self):
        dashboard_model.collection.remove()
        self.collection.remove()


    def get_all_metrics_test(self):
        self.process_collection.remove()
        plugin_model.collection.remove()


        for i in range(0, 2):
            self.process_collection.insert({"name" : "test-{0}".format(i), 'server': self.server_id})


        plugin = plugin_model.get_or_create(name='test1', server_id=self.server['_id'])

        data = {'t': 1, 'count.count_key': 2, 'second.second_key': 4, 'more.more_key': 5 }

        plugin_model.save_gauges(plugin=plugin, data=data, time=1)

        result = dashboard_metrics_model.get_all_metrics()

        for r in result:
            params = r[0].split('.')
            final_params =  dict(x.split(':') for x in params)
            assert final_params['metric_type']
        
            
            metric_type = final_params['metric_type']

            if metric_type == 'system_global':
                assert final_params['check'] in ['disk', 'memory', 'network', 'loadavg', 'cpu']
                
                if final_params['check'] == 'network':
                    assert final_params['key'] in ['i', 'o']
                
                if final_params['check']  == 'disk':
                    assert final_params['key'] == 'percent'

                if final_params['check']  == 'memory':
                    assert final_params['key'] == 'used_percent'

                if final_params['check']  == 'cpu':
                    assert final_params['key'] in ['idle', 'system', 'user', 'iowait', 'steal']

            elif metric_type == 'process_global':
                assert final_params['key'] in ['test-0', 'test-1']
                assert final_params['check'] in ['cpu', 'memory']
            elif metric_type == 'plugin_global':
                assert final_params['gauge'] in ['count', 'second', 'more']
                assert final_params['key'] in ['count_key', 'second_key', 'more_key']

        

    def get_server_metrics_test(self):

        result = dashboard_metrics_model.get_server_metrics(server_id=self.server_id)
        

        eq_(len(result), 4) # Cpu, Memory, Loadavg, Network


        self.process_collection.insert({"name" : "test", 'server': self.server_id})

        result = dashboard_metrics_model.get_server_metrics(server_id=self.server_id)

        
        eq_(len(result), 6) # Cpu, Memory, Loadavg, test:cpu, test:memory, Network
        self.process_collection.remove({'server': self.server_id})
    

    def get_or_create_metric_test(self):
        self._cleanup()
        
        dashboard_metrics_model.get_or_create_metric({'metric': 'boo', 'server_id': self.server_id})

        result = self.collection.find().count()
        eq_(result, 0)  # Don't save without dashboard_id


        dashboard_metrics_model.get_or_create_metric({'metric': 'boo', 'server_id': self.server_id,
            'dashboard_id': self.dashboard_id})

        result = self.collection.find_one()

        assert 'unique_id' in result.keys()
        assert 'server_id' in result.keys()
        
        # Todo - save only valid metrics

        self._cleanup()

        dashboard_metrics_model.get_or_create_metric({'check': 'systemd', 'server_id': 'all',
            'process_id': 'all',
            'key': 'cpu',
            'metric_type': 'process_global',
            'dashboard_id': self.dashboard_id})

        result = self.collection.find().count()
        eq_(result, 1)  # Save global process metrics


        result = self.collection.find_one()
        assert result['metric_type'] == 'process_global'
        assert result['key'] == 'cpu'
        assert result['check'] == 'systemd'
        

        self._cleanup()


        dashboard_metrics_model.get_or_create_metric({'check': 'memory', 'server_id': 'all',
            'key': 'percent',
            'metric_type': 'system_global',
            'dashboard_id': self.dashboard_id})

        result = self.collection.find().count()
        eq_(result, 1)  # Save global system metrics


        result = self.collection.find_one()
        assert result['metric_type'] == 'system_global'
        assert result['key'] == 'percent'
        assert result['check'] == 'memory'


        self._cleanup()


        dashboard_metrics_model.get_or_create_metric({'check': 'memory', 'server_id': 'all',
            'key': 'percent',
            'metric_type': 'system_global',
            'dashboard_id': self.dashboard_id})

        result = self.collection.find().count()
        eq_(result, 1)  # Save global plugin metrics


        result = self.collection.find_one()
        assert result['metric_type'] == 'system_global'
        assert result['key'] == 'percent'
        assert result['check'] == 'memory'


    def get_all_test(self):
        self._cleanup()


        # Test system metrics
        for i in range(5):
            dashboard_metrics_model.get_or_create_metric({'check': 'cpu', 'server_id': self.server_id,
                'dashboard_id': self.dashboard_id, 'account_id': self.account_id})

        result = dashboard_metrics_model.get_all()

        eq_(len(result), 0)  # Don't get anything without account/dashboard id

        result = dashboard_metrics_model.get_all(account_id=self.account_id, dashboard_id=self.dashboard_id)

        eq_(len(result), 5)  # Returns a list with values

        for r in result:
            self.assertCountEqual(set(r.keys()), 
                set(['tags', 'url', 'unit', 'utcnow', 'type', 'server_id', 'name', 'id', 'unique_id',  'metric_type', 'server_name', 'order']))
            
            assert r['type'] == 'server_metric'
            assert r['metric_type'] == 'system'
            assert r['server_name'] == self.server['name']

        dashboard_metrics_model.collection.remove()

        # Test process metrics
        for i in range(5):
            dashboard_metrics_model.get_or_create_metric({'check': 'cpu', 'server_id': self.server_id,
                'dashboard_id': self.dashboard_id, 'account_id': self.account_id,
                'process_id': self.process_id})

        result = dashboard_metrics_model.get_all(account_id=self.account_id, dashboard_id=self.dashboard_id)
        eq_(len(result), 5)  # Returns a list with values

        for r in result:
            self.assertCountEqual(set(r.keys()), 
                set(['tags', 'url', 'unit', 'utcnow', 'server_id', 'type', 'name', 'id', 'unique_id','metric_type', 'process_id', 'server_name', 'order']))

            assert r['type'] == 'server_metric'
            assert r['metric_type'] == 'process'


        dashboard_metrics_model.collection.remove()


        plugin_model.gauge_collection.remove()
        gauge = plugin_model.get_or_create_gauge_by_name(plugin=self.plugin, name='count')
        
        # Test plugin metrics
        for i in range(5):
            dashboard_metrics_model.get_or_create_metric({
                'gauge_id': gauge['_id'],
                'server_id': self.server_id,
                'dashboard_id': self.dashboard_id,
                'account_id': self.account_id,
                'plugin_id': self.plugin_id,
            })
    
        result = dashboard_metrics_model.get_all(account_id=self.account_id, dashboard_id=self.dashboard_id)
        eq_(len(result), 5) # Returns a list with values


        for r in result:
            self.assertCountEqual(set(r.keys()), set(['url', 'unit', 'utcnow','server_id', 'name', 'id', 'unique_id', 
                    'metric_type', 'plugin_id', 'type', 'tags',
                    'gauge_id', 'server_name', 'order']))

            assert r['type'] == 'server_metric'
            assert r['metric_type'] == 'plugin'
            assert r['name'] == "{0}.{1}.{2}".format(self.server['name'], self.plugin['name'], gauge['name'])

        plugin_model.gauge_collection.remove()
        


        self._cleanup()

    def get_all_grouped_by_server_name_test(self):

        self._cleanup()
        dashboard_metrics_model.collection.remove()

        # Test system metrics
        for i in range(5):
            dashboard_metrics_model.get_or_create_metric({
                'check': 'cpu', 
                'server_id': self.server_id,
                'dashboard_id': self.dashboard_id, 
                'account_id': self.account_id})

        result = dashboard_metrics_model.get_all_grouped_by_server_name(account_id=self.account_id, dashboard_id=self.dashboard_id)


        server_metrics = result['server_metrics']

        eq_(len(server_metrics), 1)

        for i, v in server_metrics.items():
            eq_(len(v['metrics']), 5)
            
            assert i == str(self.server_id)
            assert v['name'] == self.server['name']


        dashboard_metrics_model.collection.remove()


        self._cleanup()


    def delete_all_test(self):


        self._cleanup()

        for i in range(5):
            dashboard_metrics_model.get_or_create_metric({
                'metric': 'boo',
                'server_id': self.server_id,
                'dashboard_id': self.dashboard_id, 
                'account_id': self.account_id}
            )

        result = dashboard_metrics_model.get_all(account_id=self.account_id, dashboard_id=self.dashboard_id)

        eq_(len(result), 5) # Returns a list with values

        dashboard_metrics_model.delete_all(account_id=self.account_id, dashboard_id=self.dashboard_id)


        result = dashboard_metrics_model.get_all(account_id=self.account_id, dashboard_id=self.dashboard_id)
        eq_(len(result), 0) # Returns a list with values

        self._cleanup()


    def reoder_test(self):
        self._cleanup()
        
        for i in range(5):
            dashboard_metrics_model.get_or_create_metric({
                'metric': 'order-{0}'.format(i), 
                'server_id': self.server_id,
                'dashboard_id': self.dashboard_id, 
                'account_id': self.account_id}
            )

        result = dashboard_metrics_model.get_all(account_id=self.account_id, dashboard_id=self.dashboard_id)
        ordered_ids = [x['id'] for x in result]

        
        dashboard_metrics_model.update_order(dashboard_id=self.dashboard_id, new_order=ordered_ids)

        result = dashboard_metrics_model.get_all(account_id=self.account_id, dashboard_id=self.dashboard_id)

        new_order = []
        for r in result:
            new_order.append(r['id'])

        assert ordered_ids == new_order
        self._cleanup()
        
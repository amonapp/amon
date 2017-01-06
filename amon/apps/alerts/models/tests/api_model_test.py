import unittest
from nose.tools import eq_


from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.alerts.models import AlertsAPIModel
from amon.apps.processes.models import process_model
from amon.apps.plugins.models import plugin_model
from amon.apps.devices.models import volumes_model, interfaces_model


class AlertsAPIModelTest(unittest.TestCase):

    def setUp(self):
        User.objects.all().delete()
        self.user_email = 'foo@test.com'
        self.user = User.objects.create_user(password='qwerty', email=self.user_email)
        

        self.account_id = 1

        self.model = AlertsAPIModel()
        self.model.mongo.database = 'amontest'
        self.collection = self.model.mongo.get_collection('alerts')
        self.server_collection = self.model.mongo.get_collection('servers')
        self.history_collection = self.model.mongo.get_collection('alert_history')

        self.server_collection.insert({"name" : "test", 
            "key": "test_me",
            "account_id": 199999
        })
        server = self.server_collection.find_one()
        self.server_id = server['_id']


    def tearDown(self):
        self.user.delete()
        User.objects.all().delete()



    def _cleanup(self):
        self.collection.remove()
        process_model.collection.remove()
        plugin_model.collection.remove()
        interfaces_model.collection.remove()
        volumes_model.collection.remove()

        gauges_collection = plugin_model.gauge_collection.remove()


    def get_global_metrics_test(self):
        self._cleanup()

        process_name = "alertest-process"
        plugin_name = "alertest-plugin"
        process = process_model.get_or_create(server_id=self.server_id, name=process_name)
        plugin = plugin_model.get_or_create(name=plugin_name, server_id=self.server_id)
        plugin_data = {
            'count.count_first_key': 2,
            'second.second_key': 4,
            'more.more_key': 5,
            'count.count_second_key': 4
        }
        plugin_model.save_gauges(plugin=plugin, data=plugin_data, time=1)
        plugin_gauges_keys = plugin_model.get_gauge_keys_for_server(server_id=self.server_id)

        result = self.model.get_global_metrics()

        assert len(result) == 14  # 7 system + 3 process(cpu/memory/down) + 4 plugin(for every key)
        
        system_metrics = ['CPU', 'Memory', 'Loadavg', 'Disk', 'Network/inbound', 'Network/outbound', 'Not Sending Data']
        process_metrics = ['cpu', 'memory', 'down']

        for r in result:
            value = r.get('value')
            metric_dict = dict(v.split(":") for v in value.split("."))

            assert metric_dict['rule_type']
            assert metric_dict['rule_type'] in ['global', 'process_global', 'plugin_global']
            alert_type = metric_dict.get('rule_type')
    

            if alert_type == 'system':
                assert r['metric'] in system_metrics

            if alert_type == 'process_global':
                assert r['metric'] in process_metrics




    def get_server_metrics_test(self):
        self._cleanup()

        process_name = "alertest-process"
        plugin_name = "alertest-plugin"
        process = process_model.get_or_create(server_id=self.server_id, name=process_name)
        plugin = plugin_model.get_or_create(name=plugin_name, server_id=self.server_id)
        plugin_data = {
            'count.count_first_key': 2,
            'second.second_key': 4,
            'more.more_key': 5,
            'count.count_second_key': 4
        }
        plugin_model.save_gauges(plugin=plugin, data=plugin_data, time=1)
        plugin_gauges_keys = plugin_model.get_gauge_keys_for_server(server_id=self.server_id)

        volumes_model.get_or_create(server_id=self.server_id, name='get_server_metrics_volume')
        interfaces_model.get_or_create(server_id=self.server_id, name='get_server_metrics_interface')


        result = self.model.get_server_metrics(server_id=self.server_id)

        system_metrics = ['CPU', 'Memory', 'Loadavg', 'Disk', 'Network/inbound', 'Network/outbound', 'Not Sending Data']
        system_values = ["server:{0}.metric:{1}.rule_type:system".format(self.server_id, x.replace(" ", "")) for x in system_metrics]

        volumes = volumes_model.get_all_for_server(server_id=self.server_id)
        for v in volumes:
            value = "server:{0}.metric:Disk.rule_type:system.volume:{1}".format(self.server_id, v.get('name'))
            system_values.append(value)

        interfaces = interfaces_model.get_all_for_server(server_id=self.server_id)
        for i in interfaces:
            value = "server:{0}.metric:Network/inbound.rule_type:system.interface:{1}".format(self.server_id, i.get('name'))
            system_values.append(value)

            value = "server:{0}.metric:Network/outbound.rule_type:system.interface:{1}".format(self.server_id, i.get('name'))
            system_values.append(value)

        
        process_metrics = ['CPU', 'Memory']
        process_alerts_names = ["{0}.{1}".format(process_name, x.replace(" ", "")) for x in process_metrics]
        process_values = ["server:{0}.process:{1}.metric:{2}.rule_type:process".format(self.server_id, process['_id'],  x) for x in process_metrics]

        process_uptime = ['Down']
        process_uptime_alerts_names = ["{0}.{1}".format(process_name, x.replace(" ", "")) for x in process_uptime]
        process_uptime_values = ["server:{0}.process:{1}.metric:{2}.rule_type:uptime".format(self.server_id, process['_id'],  x) for x in process_uptime]

        plugin_alert_names = ["{0}.{1}".format(plugin_name, x) for x in plugin_data.keys()]
        plugin_values = []
        for plugin_gauge_key in plugin_gauges_keys:
            gauge = plugin_gauge_key.get('gauge')
            key = plugin_gauge_key.get('key')

            _id = "server:{0}.plugin:{1}.gauge:{2}.key:{3}.rule_type:plugin".format(
                self.server_id,  
                plugin['_id'], 
                gauge['_id'],
                key
            )
            plugin_values.append(_id)


        assert len(plugin_values) == 4  # All the keys from plugin_data

        for r in result:
            value = r.get('value')
            metric_dict = dict(v.split(":") for v in value.split("."))

            alert_type = metric_dict.get('rule_type')
                

            assert alert_type != None
            assert alert_type in ['system', 'process', 'plugin', 'uptime']

            if alert_type == 'system':
                assert r.get('metric') in system_metrics
                assert r.get('value') in system_values
            
            elif alert_type == 'process':
                assert r.get('metric') in ['CPU', 'Memory']
                assert r.get('name') in process_alerts_names
                assert r.get('value') in process_values
            elif alert_type == 'uptime':
                assert r.get('metric') in ['Down']
                assert r.get('name') in process_uptime_alerts_names
                assert r.get('value') in process_uptime_values

            elif alert_type == 'plugin':
                assert r.get('name') in plugin_alert_names
                assert r.get('value') in plugin_values
            else:
                assert False  # Should not be here


    def get_selected_metric_test(self):
        self._cleanup()

        example_alert_dict = {
            "above_below": "above", 
            "email_recepients": [],
            "rule_type": "global",
            "server": "all",
            "account_id": 199999,
            "period": 300,
            "metric": "CPU"
        }

        self.collection.insert(example_alert_dict)
        result = self.collection.find_one()

        
        db_result = self.model.get_selected_metric(alert=result)

        eq_(db_result, 'CPU')

        self._cleanup()

        example_alert_dict = {
            "above_below": "above", 
            "email_recepients": [],
            "rule_type": "global",
            "server": "ubuntu",
            "account_id": 199999,
            "period": 300,
            "interface": "eth1",
            "metric": "Network/inbound"
        }

        self.collection.insert(example_alert_dict)
        result = self.collection.find_one()

        
        db_result = self.model.get_selected_metric(alert=result)

        eq_(db_result, 'Network/inbound.eth1')
        

        self._cleanup()



    

import unittest
from nose.tools import eq_


from django.contrib.auth import get_user_model
from amon.apps.alerts.models import AlertsModel
from amon.apps.processes.models import process_model
from amon.apps.plugins.models import plugin_model
from amon.apps.servers.models import server_model
from amon.apps.devices.models import volumes_model, interfaces_model

User = get_user_model()


class AlertsModelTest(unittest.TestCase):

    def setUp(self):
        User.objects.all().delete()
        self.user_email = 'foo@test.com'
        self.user = User.objects.create_user(password='qwerty', email=self.user_email)
        

        self.account_id = 1

        self.model = AlertsModel()
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

    def add_initial_data_test(self):
        self._cleanup()

        default_alert = {
            "above_below": "above", 
            "email_recepients": [],
            "rule_type": "global",
            "server": "all",
            "period": 300,
            "account_id": self.account_id
        }

        # Add initial data only if this is empty
        self.collection.insert(default_alert)
        assert self.collection.find().count() == 1
        
        self.model.add_initial_data()

        assert self.collection.find().count() == 1


        self._cleanup()

        assert self.collection.find().count() == 0
        self.model.add_initial_data()


        assert self.collection.find().count() == 3
        
        self._cleanup()

    

    def get_alerts_for_plugin_test(self):
        self._cleanup()

        plugin = plugin_model.get_or_create(server_id=self.server_id, name='testplugin')
        gauge = plugin_model.get_or_create_gauge_by_name(plugin=plugin, name='gauge')

        plugin_alert = {
            "above_below": "above",     
            "rule_type": "plugin",
            "server": self.server_id,
            "gauge": gauge['_id'], 
            "plugin": plugin['_id'], 
            "account_id": self.account_id,
            "key": "testkey",
            "period": 0,
            "metric_value": 5
         }

        for i in range(0,5):
            try:
                del plugin_alert['_id']
            except:
                pass
            plugin_alert['period'] = i
            plugin_alert['metric_value'] = i+5
            self.model.collection.insert(plugin_alert)


        result = self.model.get_alerts_for_plugin(plugin=plugin)

        assert len(result) == 5
    
        self._cleanup()



    def save_alert_test(self):
        self.collection.remove()
        self.model.save({'rule': "test", 'server': self.server_id})
        eq_(self.collection.count(), 1)

    def update_test(self):
        self.collection.remove()
        self.model.save({'rule': "test" , 'server': self.server_id, 'period': 10})

        alert = self.collection.find_one()
        alert_id = str(alert['_id'])

        self.model.update({'rule': 'updated_test', 'period': 10}, alert_id)

        alert = self.collection.find_one()

        eq_(alert['rule'], 'updated_test')
    


    def mute_test(self):
        self.collection.remove()
        self.collection.insert({"name" : "test", "key": "test_me"})
        alert = self.collection.find_one()
        alert_id = str(alert['_id'])

        self.model.mute(alert_id)

        result = self.collection.find_one()
        eq_(result["mute"], True)

        self.model.mute(alert_id)

        result = self.collection.find_one()
        eq_(result["mute"], False)


    def get_mute_state_test(self):
        self.collection.remove()

        for i in range(0, 10):
            self.collection.insert({"name" : "test", "mute": True,"account_id": self.account_id})
        

        result = self.model.get_mute_state(account_id=self.account_id)
        eq_(result, False) # A toggle function -> this is the next state 

        self.collection.remove()

        for i in range(0, 10):
            self.collection.insert({"name" : "test", "mute": False,"account_id": self.account_id})
        

        result = self.model.get_mute_state(account_id=self.account_id)
        eq_(result, True) # A toggle function -> this is the next state 

    def mute_all_test(self):
        self.collection.remove()

        for i in range(0, 10):
            self.collection.insert({"name" : "test", "mute": False ,"account_id": self.account_id})

        result = self.model.mute_all(account_id=self.account_id)
        for r in self.collection.find():
            eq_(r['mute'], True)

        self.collection.remove()


        for i in range(0, 10):
            self.collection.insert({"name" : "test", "mute": True ,"account_id": self.account_id})

        result = self.model.mute_all(account_id=self.account_id)
        for r in self.collection.find():
            eq_(r['mute'], False)

        self.collection.remove()
        


    def get_alerts_test(self):
        self.collection.remove()
        self.server_collection.remove()
        self.server_collection.insert({"name" : "test", "key": "test_me"})
        server = self.server_collection.find_one()
        
        rule = { "server": server['_id'], "rule_type": 'system', 'metric': 2, 'period': 10}
        self.collection.insert(rule)
        
        rule = { "server": server['_id'], "rule_type": 'system', 'metric': 1, 'period': 10}
        self.collection.insert(rule)

        
        rules = self.model.get_alerts(type='system', server=server)

        eq_(len(rules), 2)
        self.collection.remove()


    def delete_alerts_test(self):
        self.collection.remove()
        self.collection.insert({"name" : "test", "key": "test_me"})
        rule = self.collection.find_one()

        self.model.delete(alert_id=rule['_id'])

        result = self.collection.count()
        eq_(result,0)

        self.collection.remove()


    def save_healthcheck_occurence_test(self):
        self.history_collection.remove()
        self.collection.remove()

    def save_occurence_test(self):
        self.history_collection.remove()

        self.collection.remove()
        self.collection.insert({
            "rule_type" : "custom_metric_gauge", 
            "metric_value" : 10,
            "metric_type" : "more_than",
            "period": 10
        })
        
        rule = self.collection.find_one()
        rule_id = str(rule['_id'])


        for i in range(300, 330):
            self.model.save_occurence({
                'value': 11, 
                'alert_id': rule_id, 
                'trigger': True,
                'time': i
            
            })
        trigger_result = self.history_collection.find({'alert_id': rule['_id'] , 'notify': True})
        assert trigger_result.count() == 2 # 310 and 321


    def save_health_check_occurence_test(self):

        self.history_collection.remove()

        self.server_collection.remove()
        self.server_collection.insert({'name': 'test'})
        server = self.server_collection.find_one()
        

        self.collection.remove()
        self.collection.insert({
            "rule_type" : "health_check",
            "server": server['_id'], 
            "command" : "check-http.rb", 
            "status": "critical",
            "period": 10
        })
        
        rule = self.collection.find_one()
        rule['server'] = server
        rule_id = str(rule['_id'])

        for i in range(0, 110):
            trigger_dict = {
                'value': 1, 
                'alert_id': rule_id, 
                'trigger': True,
                'time': i,
                'health_checks_data_id': 'test'
            }
            self.model.save_healtcheck_occurence(trigger=trigger_dict, server_id=server['_id'])

    
        trigger_result = self.history_collection.find({'alert_id': rule['_id'] , 'notify': True})
        
        eq_(trigger_result.count(), 10)

        for r in trigger_result.clone():
            assert r['from'] in [0, 11, 22, 33, 44, 55, 66, 77, 88, 99]
            assert r['time'] in [10, 21, 32, 43, 54, 65, 76, 87, 98, 109]
            assert r['health_checks_data_id']

        self.history_collection.remove()
        # Second test with some of the triggers set to False
        for i in range(300, 400):
            trigger = True
            if i % 2 == 1:
                trigger = False

            trigger_dict = {
                'value': 1, 
                'alert_id': rule_id, 
                'trigger': trigger,
                'time': i,
                'health_checks_data_id': 'test'
            }
            self.model.save_healtcheck_occurence(trigger=trigger_dict, server_id=server['_id'])


        trigger_result = self.history_collection.find({'alert_id': rule['_id'] , 'notify': True})
        eq_(trigger_result.count(), 0)

        
        self.history_collection.remove()


    def save_system_occurence_test(self):
        self.history_collection.remove()

        self.server_collection.remove()
        self.server_collection.insert({'name': 'test'})
        server = self.server_collection.find_one()
        

        self.collection.remove()
        self.collection.insert({
            "rule_type" : "system",
            "server": server['_id'],
            "metric_type_value" : "%",
            "metric_value" : "10",
            "metric_type" : "more_than",
            "metric" : "CPU",
            "period": 10
        })
        
        rule = self.collection.find_one()
        rule_id = str(rule['_id'])
        server_id = rule['server']


        for i in range(300, 320):
            self.model.save_system_occurence({'cpu':
            [{
                'value': 11,
                'rule': rule_id,
                'trigger': True,
                'server_id': server_id,
                'time': i
            
            }]}, server_id=server_id)

    
        trigger_result = self.history_collection.find({'alert_id': rule['_id'] , 'notify': True})
    
        eq_(trigger_result.count(), 1)  # Only 1 trigger on 400
        for r in trigger_result.clone():
            eq_(r['time'], 310)
            eq_(r['from'], 300)

    
        self.history_collection.remove()

        # Second test with some of the triggers set to False
        for i in range(300, 400):
            trigger = True
            if i % 2 == 1:
                trigger = False
            
            self.model.save_system_occurence({'cpu': 
            [{
                'value': 11, 
                'rule': rule_id, 
                'trigger': trigger,
                'server': server['_id'],
                'time': i
            
            }]}, server_id=server_id)


        trigger_result = self.history_collection.find({'alert_id': rule['_id'] , 'notify': True})
        eq_(trigger_result.count(), 0)

        
        self.history_collection.remove()


        # Try with bigger range and multiple triggers
        for i in range(300, 333):
            self.model.save_system_occurence({'cpu': 
            [{
                'value': 11, 
                'rule': rule_id, 
                'trigger': True,
                'server': server['_id'],
                'time': i
            
            }]}, server_id=server_id)

        trigger_result = self.history_collection.find({'alert_id': rule['_id'] , 'notify': True})

        eq_(trigger_result.count(), 3)

    
        for r in trigger_result.clone():
            time_list = [310, 321, 332]
            eq_(r['time'] in time_list, True)
            

        self.history_collection.remove()
        self.server_collection.remove()



    def delete_server_alerts_test(self):
        server_model.collection.remove()
        self.collection.remove()

        server_id = server_model.add('testserver')
        self.collection.insert({"rule_type" : "process",})
        self.collection.insert({"rule_type" : "system",})
        
        self.collection.insert({"rule_type" : "log", "server": server_id})
        self.collection.insert({"rule_type" : "dummy", "server":server_id})
        self.collection.insert({"rule_type" : "dummy", "server": server_id})

        self.model.delete_server_alerts(server_id)

        eq_(self.collection.count(), 2)
        self.collection.remove()


    def get_by_id_test(self):
        self.collection.remove()
        server_model.collection.remove()
        plugin_model.collection.remove()


        server_id = server_model.add('testserver')
        plugin = plugin_model.get_or_create(name='testplugin', server_id=server_id)


        self.collection.insert({
            "rule_type" : "process", 
            "server": server_id,
            "plugin": plugin['_id'], 
            'sms_recepients': [], 
            'email_recepients': [], 
            'webhooks': []}
        )
        alert = self.collection.find_one()

        alert_from_model = self.model.get_by_id(alert['_id'])
        
        assert alert_from_model['plugin'] == plugin['_id']
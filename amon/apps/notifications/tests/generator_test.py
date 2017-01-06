from django.test import TestCase

from amon.apps.servers.models import server_model
from amon.apps.processes.models import process_model
from amon.apps.notifications.generator import generate_notifications, generate_message
from amon.apps.alerts.models import alerts_model, alerts_history_model
from amon.apps.alerts.alerter import server_alerter, process_alerter, uptime_alerter


class GeneratorTests(TestCase):

    def setUp(self):

        self.account_id = 1

        server_key = server_model.add('testserver', account_id=self.account_id)
        self.server = server_model.get_server_by_key(server_key)
        self.server_id = self.server['_id']

        self.process = process_model.get_or_create(server_id=self.server_id, name='testprocess')
        self.process_id = self.process['_id']

    def tearDown(self):
        server_model.collection.remove()
        process_model.collection.remove()
        alerts_history_model.collection.remove()
        alerts_model.collection.remove()
        
    
    def generate_notifications_test(self):
        # System alert
        system_alert = {
            "above_below": "above",
            "rule_type": "system",
            "server": self.server_id,
            "account_id": self.account_id,
            "period": 0,
        }


        # CPU alert
        cpu_alert_dict = {**system_alert, 'metric': 'CPU', 'metric_value': 1, 'metric_type': "%"}
        alerts_model.collection.insert(cpu_alert_dict)

        for r in alerts_model.collection.find():
            print(r)

        data = {u'cpu': {u'system': u'1.30', u'idle': u'98.70', u'user': u'0.00', u'steal': u'0.00', u'nice': u'0.00'}}
        server_alerter.check(data, self.server)

        process_alert = {
            "above_below": "above",     
            "rule_type": "process",
            "server": self.server_id,
            "process": self.process_id, 
            "account_id": self.account_id,
            "period": 0,
        }

        cpu_alert = {**process_alert, 'metric': 'CPU', 'metric_value': 1, 'metric_type': "%"}
        alerts_model.collection.insert(cpu_alert)

        data = {'data': [{'p': self.process_id, 'c': 2, 'm': 254.0}] }
        process_alerter.check(data, self.server)

        uptime_alert = {
            "above_below": "above",
            "rule_type": "uptime",
            "server": self.server_id,
            "process": self.process_id,
            "account_id": self.account_id,
            "period": 0,
        }

        down_alert = {**uptime_alert, 'metric': 'Down', 'metric_value': 0}
        alerts_model.collection.insert(down_alert)

        data = {'data': []}
        uptime_alerter.check(data, self.server)

        result = generate_notifications()

        assert len(result) == 3

        # Assert notification dict
        system_keys = ['alert', 'server', 'metadata', 'timezone', 'trigger', 'mute', 'global_mute']
        
        process_keys = list(system_keys)
        process_keys.append('process')

        for r in result:
            rule_type = r.alert['rule_type']

            if rule_type in ['uptime', 'process']:
                assert set(r.__dict__.keys()) == set(process_keys)
            else:
                assert set(r.__dict__.keys()) == set(system_keys)



        for r in result:
            message = generate_message(notification=r)
            if r.alert['rule_type'] == 'process':
                assert message == 'Server:testserver/testprocess CPU > 1% for 0 seconds (Current value: 2.0%)'

            elif r.alert['rule_type'] == 'system':
                assert message == 'Server:testserver CPU>1% for 0 seconds (Current value: 1.3%)'
            elif r.alert['rule_type'] == 'uptime':
                assert message == 'testprocess on testserver is Down'
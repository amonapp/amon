import unittest
from nose.tools import eq_

from django.contrib.auth import get_user_model
User = get_user_model()


from amon.apps.servers.models import server_model
from amon.apps.processes.models import process_model
from amon.apps.alerts.models import alerts_model, alerts_history_model
from amon.apps.alerts.alerter import (
    server_alerter,
    process_alerter,
    uptime_alerter,
    plugin_alerter,
    health_check_alerter,
    notsendingdata_alerter
)
from amon.apps.plugins.models import plugin_model

from amon.utils.dates import unix_utc_now


class ServerAlerterTest(unittest.TestCase):

    def setUp(self):
        User.objects.all().delete()
        self.alerter = server_alerter
        self.user = User.objects.create_user(password='qwerty' , email='foo@test.com')
        self.account_id = 1

        self.server_key = server_model.add('test', account_id=self.account_id)
        self.server = server_model.get_server_by_key(self.server_key)
        self.server_id = self.server['_id']

        self.process = process_model.get_or_create(server_id=self.server_id, name='test')
        self.process_id = self.process['_id']

        self.plugin = plugin_model.get_or_create(server_id=self.server_id, name='testplugin')
        self.plugin_id = self.plugin['_id']

        self.gauge = plugin_model.get_or_create_gauge_by_name(plugin=self.plugin, name='gauge')
        self.gauge_id = self.gauge['_id']



    def tearDown(self):
        alerts_model.collection.remove()
        server_model.collection.remove()
        process_model.collection.remove()
        plugin_model.collection.remove()
        plugin_model.gauge_collection.remove()


        self.user.delete()
        User.objects.all().delete()



    def _cleanup(self):
        alerts_history_model.collection.remove()
        alerts_model.collection.remove()

    def test_global_check(self):

        self._cleanup()

        # GLOBAL ALERT
        global_alert = {
            "above_below": "above",
            "rule_type": "global",
            "server": "all",
            "account_id": self.account_id,
            "period": 0,
        }

        # CPU alert
        cpu_alert_dict = {**global_alert, 'metric': 'CPU', 'metric_value': 1, 'metric_type': "%"}
        alert_id = alerts_model.collection.insert(cpu_alert_dict)


        global_rules = alerts_model.get_global_alerts(account_id=self.account_id)

        eq_(len(global_rules), 1)


        data = {u'cpu': {u'system': u'1.30', u'idle': u'98.70', u'user': u'0.00', u'steal': u'0.00', u'nice': u'0.00'}}

        server_alerter.check(data, self.server)

        unsent_alerts = alerts_history_model.get_unsent(server_id=self.server_id)
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id

        eq_(unsent_alerts['data'].count(), 1)


    def test_system_check(self):
        self._cleanup()

        #  System alert
        system_alert = {
            "above_below": "above",
            "rule_type": "system",
            "server": self.server_id,
            "account_id": self.account_id,
            "period": 0,
        }

        # CPU alert
        cpu_alert_dict = {**system_alert, 'metric': 'CPU', 'metric_value': 1, 'metric_type': "%"}
        alert_id = alerts_model.collection.insert(cpu_alert_dict)

        rules = alerts_model.get_alerts(type='system', server=self.server)
        eq_(len(rules), 1)


        data = {u'cpu': {u'system': u'1.30', u'idle': u'98.70', u'user': u'0.00', u'steal': u'0.00', u'nice': u'0.00'}}

        server_alerter.check(data, self.server)

        unsent_alerts = alerts_history_model.get_unsent(server_id=self.server_id)
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id

        eq_(unsent_alerts['data'].count(), 1)


        self._cleanup()



    def test_process_alert(self):
        self._cleanup()

        process_alert = {
            "above_below": "above",
            "rule_type": "process",
            "server": self.server_id,
            "process": self.process_id,
            "account_id": self.account_id,
            "period": 0,
        }

        cpu_alert_dict = {**process_alert, 'metric': 'CPU', 'metric_value': 1, 'metric_type': "%"}
        alert_id = alerts_model.collection.insert(cpu_alert_dict)
        cpu_value = float(2)

        data = {'data': [{'p': self.process_id, 'c': cpu_value}]}
        process_alerter.check(data, self.server)

        unsent_alerts = alerts_history_model.get_unsent()
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id
            assert trigger['average_value'] == cpu_value


        eq_(unsent_alerts['data'].count(), 1)

        self._cleanup()

        process_alert = {
            "above_below": "above",
            "rule_type": "process_global",
            "server": 'all',
            "process": 'mongo',
            "account_id": self.account_id,
            "period": 0,
        }

        process = process_model.get_or_create(server_id=self.server_id, name='mongo')
        global_process_id = process['_id']

        cpu_alert_dict = {**process_alert, 'metric': 'CPU', 'metric_value': 1, 'metric_type': "%"}
        alert_id = alerts_model.collection.insert(cpu_alert_dict)
        cpu_value = float(2)

        data = {'data': [{'p': global_process_id, 'c': cpu_value}]}
        process_alerter.check(data, self.server)

        unsent_alerts = alerts_history_model.get_unsent()
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id
            assert trigger['average_value'] == cpu_value


        eq_(unsent_alerts['data'].count(), 1)

    def test_plugin_alert(self):
        self._cleanup()

        plugin_alert = {
            "above_below": "above",
            "rule_type": "plugin",
            "server": self.server_id,
            "gauge": self.gauge_id,
            "plugin": self.plugin_id,
            "account_id": self.account_id,
            "key": "testkey",
            "period": 0,
            "metric_value": 5
        }

        alert_id = alerts_model.collection.insert(plugin_alert)
        key_name = '{0}.testkey'.format(self.gauge['name'])
        data = {'gauges': {'bla.test': 1, key_name: 6}}

        plugin_alerter.check(data=data, plugin=self.plugin)

        unsent_alerts = alerts_history_model.get_unsent()
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id
            assert trigger['average_value'] == 6

        eq_(unsent_alerts['data'].count(), 1)

        self._cleanup()

        plugin = plugin_model.get_or_create(server_id=self.server_id, name='mongo')

        gauge = 'global_gauge.global_key'
        plugin_alert = {
            "above_below": "above",
            "rule_type": "plugin_global",
            "server": 'all',
            "plugin": 'mongo',
            "gauge": 'global_gauge',
            "key": 'global_key',
            "period": 0,
            "metric_value": 5
        }

        alert_id = alerts_model.collection.insert(plugin_alert)

        data = {'gauges': {'bla.test': 1, gauge: 6}}

        plugin_alerter.check(data=data, plugin=plugin, server=self.server)

        unsent_alerts = alerts_history_model.get_unsent()
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id
            assert trigger['average_value'] == 6

        eq_(unsent_alerts['data'].count(), 1)


    def test_uptime_alert(self):
        self._cleanup()

        uptime_alert = {
            "above_below": "above",
            "rule_type": "uptime",
            "server": self.server_id,
            "process": self.process_id,
            "account_id": self.account_id,
            "period": 0,
        }

        cpu_alert_dict = {**uptime_alert, 'metric': 'Down', 'metric_value': 0}
        alerts_model.collection.insert(cpu_alert_dict)

        data = {'data': []}
        uptime_alerter.check(data, self.server)

        unsent_alerts = alerts_history_model.get_unsent(server_id=self.server_id)
        eq_(unsent_alerts['data'].count(), 1)


        self._cleanup()


    def test_notsendingdata_alert(self):
        self._cleanup()

        now = unix_utc_now()

        uptime_alert = {
            "rule_type": "system",
            "server": self.server_id,
            "account_id": self.account_id,
            "period": 0,
        }

        cpu_alert_dict = {**uptime_alert, 'metric': 'NotSendingData'}
        alert_id = alerts_model.collection.insert(cpu_alert_dict)

        server_model.update({'last_check': now - 15}, self.server_id)
        notsendingdata_alerter.check()

        unsent_alerts = alerts_history_model.get_unsent()
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id

        eq_(unsent_alerts['data'].count(), 1)


        self._cleanup()


        now = unix_utc_now()

        uptime_alert = {
            "rule_type": "global",
            "server": "all",
            "account_id": self.account_id,
            "period": 0,
        }

        cpu_alert_dict = {**uptime_alert, 'metric': 'NotSendingData'}
        alert_id = alerts_model.collection.insert(cpu_alert_dict)

        server_model.update({'last_check': now - 15}, self.server_id)
        notsendingdata_alerter.check()

        unsent_alerts = alerts_history_model.get_unsent()
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id

        eq_(unsent_alerts['data'].count(), 1)


    def test_health_check_alert(self):
        self._cleanup()

        # Alert for 1 server
        health_check_alert = {
            "rule_type": "health_check",
            "server": self.server_id,
            "status": "critical",
            "command": "check-http.rb",
            "period": 0,
        }


        alert_id = alerts_model.collection.insert(health_check_alert)

        data = [{u'command': u'check-http.rb', u'name': u'', u'exit_code': 2}]
        health_check_alerter.check(data=data, server=self.server)


        unsent_alerts = alerts_history_model.get_unsent()
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id

        eq_(unsent_alerts['data'].count(), 1)

        self._cleanup()

        global_health_check_alert = {
            "rule_type": "health_check",
            "status": "critical",
            "command": "check-http.rb",
            "period": 0,
        }

        alert_id = alerts_model.collection.insert(global_health_check_alert)

        data = [{u'command': u'check-http.rb -u amon.cx', u'name': u'', u'exit_code': 2}]
        health_check_alerter.check(data=data, server=self.server)


        unsent_alerts = alerts_history_model.get_unsent()
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id

        eq_(unsent_alerts['data'].count(), 1)
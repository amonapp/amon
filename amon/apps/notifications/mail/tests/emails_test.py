from django.test.client import Client
from django.test import TestCase
from django.core import mail

from nose.tools import eq_

from django.contrib.auth import get_user_model
User = get_user_model()

from amon.apps.alerts.models import alerts_model, alerts_history_model
from amon.apps.servers.models import server_model
from amon.apps.processes.models import process_model
from amon.apps.alerts.alerter import (
    server_alerter,
    process_alerter,
    uptime_alerter,
    plugin_alerter,
    health_check_alerter
)
from amon.apps.notifications.mail.sender import send_notification_email
from amon.apps.plugins.models import plugin_model
from amon.apps.healthchecks.models import health_checks_results_model

from amon.apps.notifications.generator import generate_notifications
from amon.apps.notifications.models import notifications_model


class TestAlertEmails(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')
        
        self.account_id = 1

        self.c.login(username='foo@test.com', password='qwerty')

        server_key = server_model.add('test', account_id=self.account_id)
        self.server = server_model.get_server_by_key(server_key)
        self.server_id = self.server['_id']


        notifications_model.save(data={"email": "foo@test.com"}, provider_id="email")

        notifications = notifications_model.get_all_formated()
        self.notifications_list = [x['formated_id'] for x in notifications]
        self.emails = [x['email'] for x in notifications]

        self.process = process_model.get_or_create(server_id=self.server_id, name='testprocess')
        self.process_id = self.process['_id']


    def tearDown(self):
        self.c.logout()
        self.user.delete()

        server_model.collection.remove()
        process_model.collection.remove()
        plugin_model.collection.remove()
        plugin_model.gauge_collection.remove()
        notifications_model.collection.remove()
    

    def _cleanup(self):
        alerts_history_model.collection.remove()
        alerts_model.collection.remove()
        mail.outbox = []

    
    def test_global_emails(self):
        self._cleanup()

        global_alert = {
            "above_below": "above",
            "rule_type": "global",
            "server": "all",
            "account_id": self.account_id,
            "period": 0,
            "notifications": self.notifications_list
        }

        # CPU alert
        cpu_alert = {**global_alert, 'metric': 'CPU', 'metric_value': 1, 'metric_type': "%"}
        alerts_model.collection.insert(cpu_alert)

        global_rules = alerts_model.get_global_alerts(account_id=self.account_id)
        eq_(len(global_rules), 1)


        data = {u'cpu': {u'system': u'1.30', u'idle': u'98.70', u'user': u'0.00', u'steal': u'0.00', u'nice': u'0.00'}}
        server_alerter.check(data, self.server)

        unsent_alerts = alerts_history_model.get_unsent(server_id=self.server_id)
        eq_(unsent_alerts['data'].count(), 1)

        notifications = generate_notifications()
        for n in notifications:
            send_notification_email(notification=n, emails=self.emails)


        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Server: test - CPU  > 1% alert (Current value: 1.3%)')
        self.assertEqual(mail.outbox[0].to, ['foo@test.com'])


        self._cleanup()


    def test_system_emails(self):
        self._cleanup()

        system_alert = {
            "above_below": "above",
            "rule_type": "system",
            "server": self.server_id,
            "account_id": self.account_id,
            "period": 0,
            "notifications": self.notifications_list
        }

        # CPU alert
        cpu_alert = {**system_alert, 'metric': 'CPU', 'metric_value': 1, 'metric_type': "%"}
        alerts_model.collection.insert(cpu_alert)

        data =  {u'cpu': {u'system': u'1.30', u'idle': u'98.70', u'user': u'0.00', u'steal': u'0.00', u'nice': u'0.00'}}
        server_alerter.check(data, self.server)

        unsent_alerts = alerts_history_model.get_unsent(server_id=self.server_id)
        eq_(unsent_alerts['data'].count(), 1)

        notifications = generate_notifications()
        for n in notifications:
            send_notification_email(notification=n, emails=self.emails)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Server: test - CPU  > 1% alert (Current value: 1.3%)')
        self.assertEqual(mail.outbox[0].to, ['foo@test.com'])

        self._cleanup()


    def test_process_emails(self):
        self._cleanup()

        process_alert = {
            "above_below": "above",
            "rule_type": "process",

            "server": self.server_id,
            "process": self.process_id, 
            "account_id": self.account_id,
            "period": 0,
            "notifications": self.notifications_list
        }

        # CPU alert
        cpu_alert = {**process_alert, 'metric': 'CPU', 'metric_value': 1, 'metric_type': "%"}
        alerts_model.collection.insert(cpu_alert)

        data = {'data': [{'p': self.process_id, 'c': 2, 'm': 254.0}]}
        process_alerter.check(data, self.server)

        unsent_alerts = alerts_history_model.get_unsent()
        eq_(unsent_alerts['data'].count(), 1)

        notifications = generate_notifications()
        for n in notifications:
            send_notification_email(notification=n, emails=self.emails)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Server: test - testprocess/CPU > 1% alert (Current value: 2.0%)')
        self.assertEqual(mail.outbox[0].to, ['foo@test.com'])

        self._cleanup()


    def test_plugin_emails(self):
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
            "metric_value": 5,
            "notifications": self.notifications_list
        }

        alert_id = alerts_model.collection.insert(plugin_alert)
        key_name = '{0}.testkey'.format(gauge['name'])
        data = {'gauges': {'bla.test': 1, key_name: 6}}

        plugin_alerter.check(data=data, plugin=plugin)


        unsent_alerts = alerts_history_model.get_unsent()
        for trigger in unsent_alerts['data']:
            assert trigger['alert_id'] == alert_id
            assert trigger['average_value'] == 6

        eq_(unsent_alerts['data'].count(), 1)

        notifications = generate_notifications()
        for n in notifications:
            send_notification_email(notification=n, emails=self.emails)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Server: test - testplugin.gauge.testkey > 5 (Current value: 6.0)')
        self.assertEqual(mail.outbox[0].to, ['foo@test.com'])

        self._cleanup()



    def test_uptime_emails(self):
        self._cleanup()

        # GLOBAL ALERT
        uptime_alert = {
            "above_below": "above",     
            "rule_type": "uptime",
            "server": self.server_id,
            "process": self.process_id, 
            "account_id": self.account_id,
            "period": 0,
            "notifications": self.notifications_list
        }

        down_alert = {**uptime_alert, 'metric': 'Down', 'metric_value': 0}
        alerts_model.collection.insert(down_alert)

        data = {'data': []}
        uptime_alerter.check(data, self.server)

        unsent_alerts = alerts_history_model.get_unsent(server_id=self.server_id)
        eq_(unsent_alerts['data'].count(), 1)

        notifications = generate_notifications()
        for n in notifications:
            send_notification_email(notification=n, emails=self.emails)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Server: test / testprocess is Down')
        self.assertEqual(mail.outbox[0].to, ['foo@test.com'])

        self._cleanup()



    def test_health_check_emails(self):
        self._cleanup()

        health_check_alert = {
            "rule_type": "health_check",
            "server": self.server_id,
            "status": "critical",
            "command": "check-http.rb",
            "period": 0,
        }

        alert_id = alerts_model.collection.insert(health_check_alert)


        data = [{
            u'command': u'check-http.rb', 
            u'name': u'', 
            u'exit_code': 2, 
        }]
        formated_check_data = health_checks_results_model.save(data=data, server=self.server)
        health_check_alerter.check(data=formated_check_data, server=self.server)

        unsent_alerts = alerts_history_model.get_unsent(server_id=self.server_id)
        eq_(unsent_alerts['data'].count(), 1)


        notifications = generate_notifications()
        for n in notifications:
            send_notification_email(notification=n, emails=self.emails)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Server: test - check-http.rb status is CRITICAL')
        self.assertEqual(mail.outbox[0].to, ['foo@test.com'])

        self._cleanup()



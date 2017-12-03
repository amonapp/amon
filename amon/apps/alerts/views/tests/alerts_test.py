from django.test.client import Client
from django.test import TestCase
from django.urls import reverse
from nose.tools import *

from amon.apps.alerts.models import alerts_model
from django.contrib.auth import get_user_model
User = get_user_model()
from amon.apps.notifications.models import notifications_model


class TestAlertViews(TestCase):

    def setUp(self):
        User.objects.all().delete()

        self.c = Client()
        self.user = User.objects.create_user(password='qwerty', email='foo@test.com')


        self.account_id = 1
        self.c.login(username='foo@test.com', password='qwerty')
        

        self.server_collection = alerts_model.mongo.get_collection('servers')
        self.server_collection.insert({
            "name" : "test", 
            "key": "test_me",
            "account_id": self.account_id
        })
        server = self.server_collection.find_one({'account_id': self.account_id})
        self.server_id = server['_id']


        self.process_collection = alerts_model.mongo.get_collection('processes')
        self.process_collection.insert({
            "name" : "test", 
            "account_id": self.account_id
        })
        process = self.process_collection.find_one()
        self.process_id = process['_id']

        notifications_model.save(data={"email": "martin@amon.cx"}, provider_id="email")

        notifications = notifications_model.get_all_formated()
        self.notifications_list = [x['formated_id'] for x in notifications]


        notifications_model.save(data={"email": "ajax@amon.cx"}, provider_id="email")
        notifications = notifications_model.get_all_formated()
        self.updated_notifications_list = [x['formated_id'] for x in notifications]



        self.example_alert_dict = {
            "above_below": "above", 
            "email_recepients": [],
            "rule_type": "global",
            "server": "all",
            "account_id": self.account_id,
            "period": 300,
        }

    def tearDown(self):
        self.c.logout()
        self.user.delete()
        User.objects.all().delete()
        

        self.server_collection.remove()
        self.process_collection.remove()
        notifications_model.collection.remove()


    def _cleanup(self):
        alerts_model.collection.remove()


    def edit_alert_test(self):
        self._cleanup()

        self.example_alert_dict = {
            "above_below": "above", 
            "email_recepients": [],
            "rule_type": "global",
            "server": "all",
            'notifications': self.notifications_list,
            "account_id": self.account_id,
            "period": 300,
        }

        alerts_model.collection.insert(self.example_alert_dict)
        alert = alerts_model.collection.find_one()

        assert alert['notifications'] == self.notifications_list

        url = reverse('edit_alert', kwargs={'alert_id': alert['_id']})    

        data = {
            'server': 'all',
            'metric': 'server:all.metric:CPU.rule_type:global', 
            'account_id': self.account_id, 
            'metric_value':15, 
            'period': 900, 
            'notifications': self.updated_notifications_list,
            'metric_type': u'%',
            'above_below': u'below',
        }

        response = self.c.post(url, data)
        
        alert = alerts_model.collection.find_one()
        for key, value in data.items():
            if key not in ['metric']:
                eq_(alert.get(key), value)

        assert alert['notifications'] == self.updated_notifications_list

        self._cleanup()
    

    def all_alerts_test(self):
        url = reverse('alerts')    
        response = self.c.get(url)

        assert response.status_code == 200


    def add_alert_test(self):
        url = reverse('add_alert')    

        self._cleanup()    

        # Global alert
        data = {
            'server': 'all',
            'metric': 'server:all.metric:CPU.rule_type:global', 
            'account_id': self.account_id, 
            'metric_value': 0, 
            'period': 300, 
            'metric_type': u'%',
            'above_below': u'above',
            'notifications': self.notifications_list
        }

        response = self.c.post(url, data)
    
        self.assertRedirects(response, reverse('alerts'))

        db_result = alerts_model.collection.find_one()

        result_keys = {
            u'rule_type': u'global',
            u'account_id': self.account_id, 
            u'metric_value': 0, 
            u'metric': u'CPU',
            u'period': 300,
            u'server': u'all',
            u'metric_type': u'%', 
            u'above_below': u'above', 
            u'notifications': self.notifications_list, 
        }

    
        for key, value in result_keys.items():
            eq_(db_result.get(key), value)

        self._cleanup()

        # Server alert
        data = {
            'server': self.server_id,
            'metric': 'server:{0}.metric:CPU.rule_type:system'.format(self.server_id), 
            'account_id': self.account_id, 
            'metric_value': 12, 
            'period': 300, 
            'metric_type': u'%',
            'above_below': u'above',
            'notifications': self.notifications_list
        }

        response = self.c.post(url, data)


        self.assertRedirects(response, reverse('alerts'))

        db_result = alerts_model.collection.find_one()

        result_keys = {
            u'rule_type': u'system',
            u'account_id': self.account_id, 
            u'metric_value': 12, 
            u'metric': u'CPU',
            u'period': 300,
            u'server': self.server_id,
            u'metric_type': u'%', 
            u'above_below': u'above', 
            u'notifications': self.notifications_list, 
        }

        for key, value in result_keys.items():
            eq_(db_result.get(key), value)

        self._cleanup()


        # Process alert
        data = {
            'server': self.server_id,
            'metric': 'server:{0}.process:{1}.metric:Memory.rule_type:process'.format(self.server_id, self.process_id), 
            'account_id': self.account_id, 
            'metric_value': 45, 
            'period': 300, 
            'metric_type': u'%',
            'above_below': u'above',
            u'notifications': self.notifications_list, 
        }

        response = self.c.post(url, data)
        
        self.assertRedirects(response, reverse('alerts'))

        db_result = alerts_model.collection.find_one()

        result_keys = {
            u'rule_type': u'process',
            u'account_id': self.account_id, 
            u'metric_value': 45, 
            u'metric': u'Memory',
            u'period': 300,
            u'server': self.server_id,
            u'metric_type': u'%', 
            u'above_below': u'above', 
            u'notifications': self.notifications_list, 
            u'process': self.process_id,
        }

        for key, value in result_keys.items():
            eq_(db_result.get(key), value)

        self._cleanup()

        # Process global alert
        data = {
            'server': 'all',
            'metric': 'server:all.process:mongo.metric:Memory.rule_type:process_global', 
            'account_id': self.account_id, 
            'metric_value': 45, 
            'period': 300, 
            'metric_type': u'%',
            'above_below': u'above',
            u'notifications': self.notifications_list, 
        }

        response = self.c.post(url, data)
        
        self.assertRedirects(response, reverse('alerts'))

        db_result = alerts_model.collection.find_one()

        result_keys = {
            u'rule_type': u'process_global',
            u'account_id': self.account_id, 
            u'metric_value': 45, 
            u'metric': u'Memory',
            u'period': 300,
            u'server': 'all',
            u'metric_type': u'%', 
            u'above_below': u'above', 
            u'notifications': self.notifications_list, 
            u'process': 'mongo',
        }

        for key, value in result_keys.items():
            eq_(db_result.get(key), value)

        self._cleanup()


        # Down process alert
        data = {
            'server': self.server_id,
            'metric': 'server:{0}.process:{1}.metric:Down.rule_type:uptime'.format(self.server_id, self.process_id), 
            'account_id': self.account_id, 
            'metric_value': 45, 
            'period': 300, 
            'metric_type': u'%',
            'above_below': u'above',
            u'notifications': self.notifications_list, 
        }

        response = self.c.post(url, data)
        
        self.assertRedirects(response, reverse('alerts'))

        db_result = alerts_model.collection.find_one()

        result_keys = {
            u'rule_type': u'uptime',
            u'account_id': self.account_id, 
            u'metric_value': 45, 
            u'metric': u'Down',
            u'period': 300,
            u'server': self.server_id,
            u'metric_type': u'%', 
            u'above_below': u'above', 
            u'notifications': self.notifications_list, 
            u'process': self.process_id,
        }

        for key, value in result_keys.items():
            eq_(db_result.get(key), value)

        self._cleanup()

    def mute_alert_test(self):
        self._cleanup()

        alerts_model.collection.insert(self.example_alert_dict)
        alert = alerts_model.collection.find_one()

        url = reverse('mute_alert', kwargs={'alert_id': alert['_id']})    

        assert_false(alert.get('mute'))

        self.c.get(url)

        alert = alerts_model.collection.find_one()

        eq_(alert.get('mute'), True)

        self._cleanup()




    def delete_alert_test(self):
        self._cleanup()

        alerts_model.collection.insert(self.example_alert_dict)
        alert = alerts_model.collection.find_one()

        assert_true(alert)

        url = reverse('delete_alert', kwargs={'alert_id': alert['_id']})    
        self.c.get(url)

        alert = alerts_model.collection.find().count()

        eq_(alert, 0)

        self._cleanup()
        

    
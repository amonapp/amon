from django.test import TestCase
from nose.tools import eq_

from amon.apps.notifications.webhooks.sender import generate_webhook_data
from amon.utils import AmonStruct

class WebhookGeneratorTests(TestCase):

    
    def generate_notifications_test(self):
        notification = AmonStruct()


        # Structure
        hook_values = {
            'server': ['name'],
            'process': ['name'],
            'message': ['test'],
            'trigger': ['from', 'average_value', 'to'],
            'alert': ['rule_type', 'metric', 'period','metric_type', 'metric_value', 'above_below', 'key']
        }

        notification.server = {'name': 'test'}
        notification.process = {'name': 'process'}
        notification.alert = {'rule_type': 'process', 'metric': 'CPU', 'period': 10, 'above_below': 'above', 'metric_value': "%"}
        notification.metadata = {}
        notification.timezone = 'UTC'
        notification.trigger = {'from': 1, 'time': 10, 'average_value': 100}
        notification.mute = False



        result = generate_webhook_data(notification=notification)
        

        assert set(result.keys()) == set(hook_values.keys())

        for k, v in result.items():
            if k != 'message':
                assert set(hook_values[k]) == set(result[k].keys())
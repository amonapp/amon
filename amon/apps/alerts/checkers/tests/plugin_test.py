from amon.apps.alerts.checkers.plugin import PluginAlerts
from nose.tools import eq_
import unittest

class PluginAlertsTest(unittest.TestCase):

    def setUp(self):
        self.plugin_alerts = PluginAlerts()

    def check_test(self):
        data = {u'myplugin.test_above': u'40.0',  u'time': 1327169023}
        rule = {'metric_value': 39, 'above_below': 'above', 'gauge_data': {'name': 'myplugin'}, '_id':'test', 'key': 'test_above'}
        alert =  self.plugin_alerts.check(data, rule=rule)
        eq_(alert['trigger'], True)

        data = {u'myplugin.test_below': u'39.9',  u'time': 1327169023}
        rule = {'metric_value': 40, 'above_below': 'below', 'gauge_data': {'name': 'myplugin'}, '_id':'test', 'key': 'test_below'}
        alert =  self.plugin_alerts.check(data, rule=rule)
        eq_(alert['trigger'], True)



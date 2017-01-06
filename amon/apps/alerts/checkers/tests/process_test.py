from amon.apps.alerts.checkers.process import ProcessAlerts
from nose.tools import eq_
import unittest

class ProcessAlertsTest(unittest.TestCase):

    def setUp(self):
        self.process_alerts = ProcessAlerts()

    def check_memory_test(self):
        data = {u'm': u'40.0',  u'time': 1327169023}
        rule = {'metric_value': 39, 'above_below': 'above', 'metric_type': 'MB','process': 'test', '_id':'test', 'check': 'Memory'}
        alert =  self.process_alerts.check(data, rule=rule)
        eq_(alert['trigger'], True)

        data = {u'm': u'39.9',  u'time': 1327169023}
        rule = {'metric_value': 40, 'above_below': 'below', 'metric_type': 'MB','process': 'test', '_id':'test', 'check': 'Memory'}
        alert =  self.process_alerts.check(data, rule=rule)
        eq_(alert['trigger'], True)

        
    def check_cpu_test(self):
        data = {u'c': u'40.0', u'time': 1327169023}
        rule = {'metric_value': 39, 'above_below': 'above', 'metric_type': '%','process': 'test', '_id':'test' , 'check': 'CPU'}
        alert =  self.process_alerts.check(data, rule=rule)
        eq_(alert['trigger'], True)

        data = { u'c': u'39.99', u'time': 1327169023}
        rule = {'metric_value': 40, 'above_below': 'below', 'metric_type': '%','process': 'test', '_id':'test' , 'check': 'CPU'}
        alert =  self.process_alerts.check(data, rule=rule)
        eq_(alert['trigger'], True)



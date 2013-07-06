from amonone.alerts.process import ProcessAlerts
from nose.tools import eq_
import unittest

class ProcessAlertsTest(unittest.TestCase):

    def setUp(self):
        self.process_alerts = ProcessAlerts()

    def check_memory_test(self):
        data = {u'memory:mb': u'40.0',  u'time': 1327169023}
        rule = {'metric_value': 39, 'above_below': 'above', 'metric_type': 'MB','process': 'test', '_id':'test'}
        alert =  self.process_alerts.check_memory(rule, data)
        eq_(alert, True)

        data = {u'memory:mb': u'39.9',  u'time': 1327169023}
        rule = {'metric_value': 40, 'above_below': 'below', 'metric_type': 'MB','process': 'test', '_id':'test'}
        alert =  self.process_alerts.check_memory(rule, data)
        eq_(alert, True)

        
    def check_cpu_test(self):
        data = {u'cpu:%': u'40.0', u'time': 1327169023}
        rule = {'metric_value': 39, 'above_below': 'above', 'metric_type': '%','process': 'test', '_id':'test'}
        alert =  self.process_alerts.check_cpu(rule, data)
        eq_(alert, True)

        data = { u'cpu:%': u'39.99', u'time': 1327169023}
        rule = {'metric_value': 40, 'above_below': 'below', 'metric_type': '%','process': 'test', '_id':'test'}
        alert =  self.process_alerts.check_cpu(rule, data)
        eq_(alert, True)



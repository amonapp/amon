from amonone.alerts.system import SystemAlerts
from nose.tools import eq_
import unittest

class SystemAlertsTest(unittest.TestCase):

    def setUp(self):
        self.system_alerts = SystemAlerts()

    def check_memory_test(self):
        data = {u'memory:free:mb': 1, u'memory:total:mb': 102, u'memory:used:mb': 101}
        rule = {'metric_value': 100, 'above_below': 'above', 'metric_type': 'MB', '_id':'test'}
        alert =  self.system_alerts.check_memory(rule, data)
        eq_(alert, True)

        data = {u'memory:free:mb': 101, u'memory:total:mb': 102, u'memory:used:mb': 1}
        rule = {'metric_value': 2, 'above_below': 'below', 'metric_type': 'MB', "_id": "test"}
        alert =  self.system_alerts.check_memory(rule, data)
        eq_(alert, True)

        data = {u'memory:free:mb': 49, u'memory:total:mb': 100, u'memory:used:%': 49}
        rule = {'metric_value': 50, 'above_below': 'below', 'metric_type': '%', "_id": "test"}
        alert =  self.system_alerts.check_memory(rule, data)
        eq_(alert, True)

        data = {u'memory:free:mb': 51, u'memory:total:mb': 100,  u'memory:used:%': 51}
        rule = {'metric_value': 50, 'above_below': 'above', 'metric_type': '%', "_id": "test"}
        alert =  self.system_alerts.check_memory(rule, data)
        eq_(alert, True)

    def check_cpu_test(self):
        data = {u'idle': 89} # utilization 11.00
        rule = {'metric_value': 10, 'above_below': 'above', 'metric_type': '%', "_id": "test"}
        alert =  self.system_alerts.check_cpu(rule, data)
        eq_(alert, True)

        data = {u'idle': 91} # utilization 9.0
        rule = {'metric_value': 10, 'above_below': 'above', 'metric_type': '%', "_id": "test"}
        alert =  self.system_alerts.check_cpu(rule, data)
        eq_(alert, None)

        data = {u'idle': 89} # utilization 11.00, "_id": "test"}
        rule = {'metric_value': 10, 'above_below': 'below', 'metric_type': '%', "_id": "test"}
        alert =  self.system_alerts.check_cpu(rule, data)
        eq_(alert, None)

        data = {u'idle': 91} # utilization 9.0
        rule = {'metric_value': 10, 'above_below': 'below', 'metric_type': '%', "_id": "test"}
        alert =  self.system_alerts.check_cpu(rule, data)
        eq_(alert, True)

    def check_disk_test(self):
        data = {'sda1': {u'percent': 60, u'used': '6G'}}
        rule = {'metric_value': 55, 'above_below': 'above', 
                'metric_type': '%','metric_options': 'sda1', "_id": "test"}
        alert =  self.system_alerts.check_disk(rule, data)
        eq_(alert, True)

        data = {'sda1': {u'percent': 60, u'used': '6G'}}
        rule = {'metric_value': 61, 'above_below': 'below', 
                'metric_type': '%','metric_options': 'sda1', "_id": "test"}
        alert =  self.system_alerts.check_disk(rule, data)
        eq_(alert, True)

        data = {'sda1': {u'used': '6G'}}
        rule = {'metric_value': 5.9, 'above_below': 'above', 
                'metric_type': 'GB','metric_options': 'sda1', "_id": "test"}
        alert =  self.system_alerts.check_disk(rule, data)
        eq_(alert, True)

        data = {'sda1': {u'used': '6G'}}
        rule = {'metric_value': 6.1, 'above_below': 'below', 
                'metric_type': 'GB','metric_options': 'sda1', "_id": "test"}
        alert =  self.system_alerts.check_disk(rule, data)
        eq_(alert, True)


        data = {'sda1': {u'used': '6G'}} # 6144 MB
        rule = {'metric_value': 6143, 'above_below': 'above', 
                'metric_type': 'MB','metric_options': 'sda1', "_id": "test"}
        alert =  self.system_alerts.check_disk(rule, data)
        eq_(alert, True)

        data = {'sda1': {u'used': '6G'}} # 6144 MB
        rule = {'metric_value': 6145, 'above_below': 'below', 
                'metric_type': 'MB','metric_options': 'sda1', "_id": "test"}
        alert =  self.system_alerts.check_disk(rule, data)
        eq_(alert, True)


    def check_loadavg_test(self):
        data = {u'minute': 1}
        rule = {'metric_value': 0.9, 'above_below': 'above', 'metric_options': 'minute',"_id": "test"}
        alert =  self.system_alerts.check_loadavg(rule, data)
        eq_(alert, True)

        data = {u'minute': 1}
        rule = {'metric_value': 1.1, 'above_below': 'below', 'metric_options': 'minute',"_id": "test"}
        alert =  self.system_alerts.check_loadavg(rule, data)
        eq_(alert, True)

        data = {u'five_minutes': 1}
        rule = {'metric_value': 0.9, 'above_below': 'above', 'metric_options': 'five_minutes',"_id": "test"}
        alert =  self.system_alerts.check_loadavg(rule, data)
        eq_(alert, True)

        data = {u'five_minutes': 1}
        rule = {'metric_value': 1.1, 'above_below': 'below', 'metric_options': 'five_minutes',"_id": "test"}
        alert =  self.system_alerts.check_loadavg(rule, data)
        eq_(alert, True)

        data = {u'fifteen_minutes': 1}
        rule = {'metric_value': 0.9, 'above_below': 'above', 'metric_options': 'fifteen_minutes',"_id": "test"}
        alert =  self.system_alerts.check_loadavg(rule, data)
        eq_(alert, True)

        data = {u'fifteen_minutes': 1}
        rule = {'metric_value': 1.1, 'above_below': 'below', 'metric_options': 'fifteen_minutes',"_id": "test"}
        alert =  self.system_alerts.check_loadavg(rule, data)
        eq_(alert, True)
        

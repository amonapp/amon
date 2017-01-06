from amon.apps.alerts.checkers.system import SystemAlerts
from nose.tools import eq_
import unittest

class SystemAlertsTest(unittest.TestCase):

    def check_memory_test(self):
        system_alerts = SystemAlerts()
        data = {u'free_mb': 1, u'total_mb': 102, u'used_mb': 101}
        rule = {'metric_value': 100, 'above_below': 'above', 'metric_type': 'MB', '_id':'test'}
        system_alerts.check_memory(rule, data)
        eq_(system_alerts.alerts['memory'][0]['trigger'], True)


        system_alerts = SystemAlerts()
        data = {u'free_mb': 101, u'total_mb': 102, u'used_mb': 1}
        rule = {'metric_value': 2, 'above_below': 'below', 'metric_type': 'MB', "_id": "test"}
        system_alerts.check_memory(rule, data)
        eq_(system_alerts.alerts['memory'][0]['trigger'], True)


        system_alerts = SystemAlerts()
        data = {u'free_mb': 49, u'total_mb': 100, u'used_percent': 49}
        rule = {'metric_value': 50, 'above_below': 'below', 'metric_type': '%', "_id": "test"}
        system_alerts.check_memory(rule, data)
        eq_(system_alerts.alerts['memory'][0]['trigger'], True)


        system_alerts = SystemAlerts()
        data = {u'free_mb': 51, u'total_mb': 100, u'used_percent': 51}
        rule = {'metric_value': 50, 'above_below': 'above', 'metric_type': '%', "_id": "test"}
        system_alerts.check_memory(rule, data)
        eq_(system_alerts.alerts['memory'][0]['trigger'], True)


        # Trigger false, still return the data
        system_alerts = SystemAlerts()
        data = {u'free_mb': 50, u'total_mb': 100, u'used_mb': 50}
        rule = {'metric_value': 49, 'above_below': 'below', 'metric_type': 'MB', "_id": "test"}
        system_alerts.check_memory(rule, data)
        eq_(system_alerts.alerts['memory'][0]['trigger'], False)



    def check_cpu_test(self):
        system_alerts = SystemAlerts()
        data = {u'idle': 89}  # utilization 11.00
        rule = {'metric_value': 10, 'above_below': 'above', 'metric_type': '%', "_id": "test"}
        system_alerts.check_cpu(rule, data)
        eq_(system_alerts.alerts['cpu'][0]['trigger'], True)


        system_alerts = SystemAlerts()
        data = {u'idle': 91}  # utilization 9.0
        rule = {'metric_value': 10, 'above_below': 'above', 'metric_type': '%', "_id": "test"}
        system_alerts.check_cpu(rule, data)
        eq_(system_alerts.alerts['cpu'][0]['trigger'], False)

        system_alerts = SystemAlerts()
        data = {u'idle': 89}  # utilization 11.00, "_id": "test"}
        rule = {'metric_value': 10, 'above_below': 'below', 'metric_type': '%', "_id": "test"}
        system_alerts.check_cpu(rule, data)
        eq_(system_alerts.alerts['cpu'][0]['trigger'], False)

        system_alerts = SystemAlerts()
        data = {u'idle': 91}  # utilization 9.0
        rule = {'metric_value': 10, 'above_below': 'below', 'metric_type': '%', "_id": "test"}
        system_alerts.check_cpu(rule, data)
        eq_(system_alerts.alerts['cpu'][0]['trigger'], True)

    def check_disk_test(self):
        system_alerts = SystemAlerts()
        data = {'sda1': {u'percent': 60, u'used': '6G'}}
        rule = {'metric_value': 55, 'above_below': 'above',
                'metric_type': '%','volume': 'sda1', "_id": "test"}
        system_alerts.check_disk(rule, data)
        eq_(system_alerts.alerts['disk'][0]['trigger'], True)


        system_alerts = SystemAlerts()
        data = {'sda1': {u'percent': 60, u'used': '6G'}}
        rule = {'metric_value': 61, 'above_below': 'below',
                'metric_type': '%','volume': 'sda1', "_id": "test"}
        system_alerts.check_disk(rule, data)
        eq_(system_alerts.alerts['disk'][0]['trigger'], True)

        system_alerts = SystemAlerts()
        data = {'sda1': {u'used': '6G'}}
        rule = {'metric_value': 5.9, 'above_below': 'above',
                'metric_type': 'GB','volume': 'sda1', "_id": "test"}
        system_alerts.check_disk(rule, data)
        eq_(system_alerts.alerts['disk'][0]['trigger'], True)

        system_alerts = SystemAlerts()
        data = {'sda1': {u'used': '6G'}}
        rule = {'metric_value': 6.1, 'above_below': 'below',
                'metric_type': 'GB','volume': 'sda1', "_id": "test"}
        system_alerts.check_disk(rule, data)
        eq_(system_alerts.alerts['disk'][0]['trigger'], True)

        system_alerts = SystemAlerts()
        data = {'sda1': {u'used': '6G'}}  # 6144 MB
        rule = {'metric_value': 6143, 'above_below': 'above',
                'metric_type': 'MB','volume': 'sda1', "_id": "test"}
        system_alerts.check_disk(rule, data)
        eq_(system_alerts.alerts['disk'][0]['trigger'], True)

        system_alerts = SystemAlerts()
        data = {'sda1': {u'used': '6G'}}  # 6144 MB
        rule = {'metric_value': 6145, 'above_below': 'below',
                'metric_type': 'MB','volume': 'sda1', "_id": "test"}
        system_alerts.check_disk(rule, data)
        eq_(system_alerts.alerts['disk'][0]['trigger'], True)


        # Check the new golang agent
        system_alerts = SystemAlerts()
        data = [{"name": "sda1", "used": "6G"}]  # 6144 MB
        rule = {'metric_value': 6145, 'above_below': 'below',
                'metric_type': 'MB','volume': 'sda1', "_id": "test"}
        system_alerts.check_disk(rule, data)
        eq_(system_alerts.alerts['disk'][0]['trigger'], True)


        # Trigger False, return the data
        system_alerts = SystemAlerts()
        data = {'sda1': {u'used': '6G'}}  # 6144 MB
        rule = {'metric_value': 6140, 'above_below': 'below',
                'metric_type': 'MB','volume': 'sda1', "_id": "test"}
        system_alerts.check_disk(rule, data)
        eq_(system_alerts.alerts['disk'][0]['trigger'], False)


        # Different volume, No incoming data
        system_alerts = SystemAlerts()
        data = {'sda1': {u'used': '6G'}}  # 6144 MB
        rule = {'metric_value': 6140, 'above_below': 'below',
                'metric_type': 'MB','volume': 'sda2', "_id": "test"}
        system_alerts.check_disk(rule, data)
        assert len(system_alerts.alerts) == 0


    def check_network_test(self):
        system_alerts = SystemAlerts()
        data = {u'eth1-inbound': {u'inbound': u'100', u'outbound': u'0.00'}}
        rule = {'metric_value': 55, 'above_below': 'above', "_id": "test", "metric": "Network/inbound"}
        system_alerts.check_network(rule, data)
        eq_(system_alerts.alerts['network'][0]['trigger'], True)
        eq_(system_alerts.alerts['network'][0]['interface'], 'eth1-inbound')


        system_alerts = SystemAlerts()
        data = {u'eth1': {u'inbound': u'45', u'outbound': u'0.00'}}
        rule = {'metric_value': 55, 'above_below': 'above', "_id": "test", "metric": "Network/inbound"}
        system_alerts.check_network(rule, data)
        eq_(system_alerts.alerts['network'][0]['trigger'], False)

        system_alerts = SystemAlerts()
        data = {u'eth1-outbound': {u'inbound': u'1', u'outbound': u'65'}}
        rule = {'metric_value': 55, 'above_below': 'above', "_id": "test", "metric": "Network/outbound"}
        system_alerts.check_network(rule, data)
        eq_(system_alerts.alerts['network'][0]['trigger'], True)
        eq_(system_alerts.alerts['network'][0]['interface'], 'eth1-outbound')


        system_alerts = SystemAlerts()
        data = {u'eth1': {u'inbound': u'1', u'outbound': u'45'}}
        rule = {'metric_value': 55, 'above_below': 'above', "_id": "test", "metric": "Network/outbound"}
        system_alerts.check_network(rule, data)
        eq_(system_alerts.alerts['network'][0]['trigger'], False)

        # Check the new golang agent
        system_alerts = SystemAlerts()
        data = [{"name": "eth1", u'inbound': u'1', u'outbound': u'45'}]
        rule = {'metric_value': 55, 'above_below': 'above', "_id": "test", "metric": "Network/outbound"}
        system_alerts.check_network(rule, data)
        eq_(system_alerts.alerts['network'][0]['trigger'], False)


        # Check the new golang agent
        system_alerts = SystemAlerts()
        data = [{"name": "eth1", u'inbound': u'1', u'outbound': u'45'}]
        rule = {'metric_value': 55, 'above_below': 'above', "_id": "test", "metric": "Network/outbound", "interface": "eth2"}
        system_alerts.check_network(rule, data)
        assert len(system_alerts.alerts) == 0



    def check_loadavg_test(self):
        system_alerts = SystemAlerts()
        data = {u'minute': 1, u'five_minutes': 1, u'fifteen_minutes': 1}
        rule = {'metric_value': 0.9, 'above_below': 'above', 'metric_options': 'minute',"_id": "test"}
        system_alerts.check_loadavg(rule, data)
        eq_(system_alerts.alerts['loadavg'][0]['trigger'], True)

        system_alerts = SystemAlerts()
        data = {u'minute': 1, u'five_minutes': 1, u'fifteen_minutes': 1}
        rule = {'metric_value': 1.1, 'above_below': 'below', 'metric_options': 'minute',"_id": "test"}
        system_alerts.check_loadavg(rule, data)
        eq_(system_alerts.alerts['loadavg'][0]['trigger'], True)

        system_alerts = SystemAlerts()
        data = {u'minute': 1, u'five_minutes': 1, u'fifteen_minutes': 1}
        rule = {'metric_value': 0.9, 'above_below': 'above', 'metric_options': 'five_minutes',"_id": "test"}
        system_alerts.check_loadavg(rule, data)
        eq_(system_alerts.alerts['loadavg'][0]['trigger'], True)

        system_alerts = SystemAlerts()
        data = {u'minute': 1 , u'five_minutes': 1, u'fifteen_minutes': 1}
        rule = {'metric_value': 1.1, 'above_below': 'below', 'metric_options': 'five_minutes',"_id": "test"}
        system_alerts.check_loadavg(rule, data)
        eq_(system_alerts.alerts['loadavg'][0]['trigger'], True)

        system_alerts = SystemAlerts()
        data = {u'minute': 1 , u'five_minutes': 1, u'fifteen_minutes': 1}
        rule = {'metric_value': 0.9, 'above_below': 'above', 'metric_options': 'fifteen_minutes',"_id": "test"}
        system_alerts.check_loadavg(rule, data)
        eq_(system_alerts.alerts['loadavg'][0]['trigger'], True)

        system_alerts = SystemAlerts()
        data = {u'minute': 1 , u'five_minutes': 1, u'fifteen_minutes': 1}
        rule = {'metric_value': 1.1, 'above_below': 'below', 'metric_options': 'fifteen_minutes',"_id": "test"}
        system_alerts.check_loadavg(rule, data)
        eq_(system_alerts.alerts['loadavg'][0]['trigger'], True)


        # Trigger false
        system_alerts = SystemAlerts()
        data = {u'minute': 1 , u'five_minutes': 1, u'fifteen_minutes': 1}
        rule = {'metric_value': 0.9, 'above_below': 'below', 'metric_options': 'fifteen_minutes',"_id": "test"}
        system_alerts.check_loadavg(rule, data)
        eq_(system_alerts.alerts['loadavg'][0]['trigger'], False)

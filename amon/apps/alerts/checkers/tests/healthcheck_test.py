from amon.apps.alerts.checkers.healthcheck import HealthCheckAlertChecker
from nose.tools import eq_
import unittest

class HealthChecksAlertsTest(unittest.TestCase):

    def setUp(self):
        self.health_check_alerts = HealthCheckAlertChecker()

    def test_check_invalid(self):

        # Alert for specific check
        for i in range(1, 2):
            exit_codes = {0: "ok", 1: "warning", 2: "critical"}
            exit_status = exit_codes[i]
            
            data = {
                u'output': u'CheckBanner CRITICAL',
                u'command': u'check-something.rb', 
                u'exit_code': i
            }
            rule = {
                "status" : 2,
                "param" : "-u https://amon.cx",
                "command" : "check-http.rb",
                "_id": "test"
            }
            alert =  self.health_check_alerts.check(data=data, rule=rule)

            self.assertFalse(alert)


    def test_check_valid(self):
        # Alert for specific check
        for i in range(1, 2):
            exit_codes = {0: "ok", 1: "warning", 2: "critical"}
            exit_status = exit_codes[i]
            
            data = {
                u'output': u'CheckBanner CRITICAL',
                u'command': u'check-http.rb -u https://amon.cx', 
                u'exit_code': i
            }
            rule = {
                "status" : exit_status,
                "param" : "-u https://amon.cx",
                "command" : "check-http.rb",
                "_id": "test"
            }
            alert =  self.health_check_alerts.check(data=data, rule=rule)
            eq_(alert['trigger'], True)

        # Global alert
        for i in range(1, 2):
            exit_codes = {0: "ok", 1: "warning", 2: "critical"}
            exit_status = exit_codes[i]
            

            data = {
                u'output': u'CheckBanner CRITICAL',
                u'command': u'check-http.rb', 
                u'exit_code': i
            }

            rule = {
                "status" : exit_status,
                "param" : "",
                "command" : "check-http.rb",
                "_id": "test"
            }
            alert =  self.health_check_alerts.check(data=data, rule=rule)
            eq_(alert['trigger'], True)



            data_different_input = {
                u'output': u'CheckBanner CRITICAL',
                u'command': u'check-http.rb -u something - w else', 
                u'exit_code': i
            }
            
            rule = {
                "status" : exit_status,
                "param" :  "",
                "command" : "check-http.rb",
                "_id": "test"
            }
            alert =  self.health_check_alerts.check(data=data_different_input, rule=rule)
            eq_(alert['trigger'], True)



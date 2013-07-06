from amonone.sms.sender import render_template
from nose.tools import *
import unittest

# class SMSRenderTest(unittest.TestCase):

# 	def render_test(self):
# 		alert = {"rule_type" : "server", "metric_type_value" : "%", "threshold" : "10",
# 				"metric_value" : "10", "metric_type" : "more_than", "metric" : "CPU",
# 				"metric_options" : "", "server_name": "test"} 
# 		result = render_template(alert=alert, template='server')
# 		eq_(result, u'test:cpu > 10% \n')
		
# 		alert = {"rule_type" : "server", "metric_type_value" : "MB", "threshold" : "10",
# 				"metric_value" : "10", "metric_type" : "more_than", "metric" : "Memory",
# 				"metric_options" : "", "server_name": "test"} 
# 	   result = render_template(alert=alert, template='server')
# 		eq_(result, u'test:memory > 10MB \n')
		
# 		alert = {"rule_type" : "server", "metric_type_value" : "GB", "threshold" : "10",
# 				"metric_value" : "10", "metric_type" : "more_than", "metric" : "Disk",
# 				"metric_options" : "sda1", "server_name": "test"} 
# 	   result = render_template(alert=alert, template='server')
# 		eq_(result, u'test:disk(sda1) > 10GB \n')
		
# 		alert = {"rule_type" : "server", "metric_type_value" : "", "threshold" : "10",
# 				"metric_value" : "10", "metric_type" : "more_than", "metric" : "Loadavg",
# 				"metric_options" : "minute", "server_name": "test"} 
# 	   result = render_template(alert=alert, template='server')
# 		eq_(result, u'test:loadavg(minute) > 10 \n')
		






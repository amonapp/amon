import unittest
from nose.tools import * 

from amonone.alerts.alerter import ServerAlerter
from amonone.web.apps.core.models import server_model
from amonone.web.apps.alerts.models import alerts_model


test_system_data = {u'memory': { u'memory:free:mb': 800, u'memory:total:mb': 2012, u'memory:used:mb': 1200}}
rule ={"rule_type" : "server", "metric_type" : "MB", 
		"metric_value" : "1000", "above_below" : "above", "metric" : "Memory", "server": ""}


class ServerAlerterTest(unittest.TestCase):

	def setUp(self):
		self.alerter = ServerAlerter()
		

	def test_check(self):
		alerts_model.collection.remove()
		server_model.collection.remove()
		server_model.collection.insert({"server_name" : "test", "key": "test_me"})
		server = server_model.collection.find_one()
		server_id = str(server['_id'])

		rule['server'] = server_id
		alerts_model.save(rule)

		check = self.alerter.check(data=test_system_data, server=server, alert_type='server')
		eq_(check['memory'][0]['rule'], str(rule['_id']))



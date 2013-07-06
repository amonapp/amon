import unittest
from nose.tools import eq_
from amonone.web.apps.alerts.models import AlertsModel, AlertGroupsModel


class AlertGroupsModelTest(unittest.TestCase):

	def setUp(self):
		self.model = AlertGroupsModel()
		self.collection = self.model.mongo.get_collection('alert_groups')
		self.servers_collection = self.model.mongo.get_collection('servers')
		self.history_collection = self.model.mongo.get_collection('alert_groups_history')
		self.alerts_collection = self.model.mongo.get_collection('alerts')


	def save_test(self):
		self.collection.remove()
		self.model.save({'name': 'group'})
		result = self.collection.find_one()

		eq_(result['name'], 'group')
		

	def get_alerts_for_group_test(self):
		self.alerts_collection.remove()

		self.alerts_collection.insert({'group': 'test', 'rule_type': 'group'})
		self.alerts_collection.insert({'group': 'test', 'rule_type': 'group'})
		
		result = self.model.get_alerts_for_group('test')

		eq_(len(result), 2)


	def save_occurence_test(self):
		self.collection.remove()
		self.history_collection.remove()
		self.model.save({'name': 'group'})
		group = self.collection.find_one()
		group_id = str(group['_id'])

		self.servers_collection.remove()
		self.servers_collection.insert({'alert_group': group_id, 'name': 'test'})

		server = self.servers_collection.find_one()

		rule = {
			"metric_value": "0.1",
			"metric": "CPU",
			"metric_type": "%",
			"threshold": "1",
			"above_below": "above",
			"rule_type": "group",
			"group": group_id,
		}

		self.alerts_collection.remove()
		self.alerts_collection.insert(rule)

		rule = self.alerts_collection.find_one()
		rule_id = str(rule['_id'])

		alerts = {'cpu': [{'alert_on': 14, 'rule': rule_id}]}
		self.model.save_occurence(alerts, server)

		alerts = {'cpu': [{'alert_on': 25, 'rule': rule_id}]}
		self.model.save_occurence(alerts, server)

		result = self.history_collection.find_one()
		
		eq_(len(result['history']), 2)
		eq_(result['server'], server['_id'])
		eq_(result['alert'], rule['_id'])


	def clear_alert_history_test(self):
		self.collection.remove()
		self.history_collection.remove()
		self.model.save({'name': 'group'})
		group = self.collection.find_one()
		group_id = str(group['_id'])

		self.servers_collection.remove()
		self.servers_collection.insert({'alert_group': group_id, 'name': 'test'})

		server = self.servers_collection.find_one()

		rule = {
			"metric_value": "0.1",
			"metric": "CPU",
			"metric_type": "%",
			"threshold": "1",
			"above_below": "above",
			"rule_type": "group",
			"group": group_id,
		}

		self.alerts_collection.remove()
		self.alerts_collection.insert(rule)

		rule = self.alerts_collection.find_one()
		rule_id = str(rule['_id'])

		alerts = {'cpu': [{'alert_on': 14, 'rule': rule_id}]}
		self.model.save_occurence(alerts, server)

		result = self.history_collection.find_one()
		
		eq_(len(result['history']), 1)


		self.model.clear_alert_history(rule['_id'], server['_id'], {})
		result = self.history_collection.find_one()
		
		eq_(result['history'], [])


	def get_history_test(self):
		self.collection.remove()
		self.history_collection.remove()
		self.model.save({'name': 'group'})
		group = self.collection.find_one()
		group_id = str(group['_id'])

		self.servers_collection.remove()
		self.servers_collection.insert({'alert_group': group_id, 'name': 'test'})

		server = self.servers_collection.find_one()

		rule = {
			"metric_value": "0.1",
			"metric": "CPU",
			"metric_type": "%",
			"threshold": "1",
			"above_below": "above",
			"rule_type": "group",
			"group": group_id,
		}

		self.alerts_collection.remove()
		self.alerts_collection.insert(rule)

		rule = self.alerts_collection.find_one()
		rule_id = str(rule['_id'])

		alerts = {'cpu': [{'alert_on': 14, 'rule': rule_id}]}
		self.model.save_occurence(alerts, server)

		history = self.model.get_history(rule['_id'], server['_id'])

		eq_(len(history), 1)


	def delete_alerts_for_group_test(self):
		self.alerts_collection.remove()
		self.collection.remove()
		self.history_collection.remove()
		self.model.save({'name': 'group'})
		group = self.collection.find_one()
		group_id = str(group['_id'])

		self.servers_collection.remove()
		self.servers_collection.insert({'alert_group': group_id, 'name': 'test'})

		server = self.servers_collection.find_one()

		rule = {
			"metric_value": "0.1",
			"metric": "CPU",
			"metric_type": "%",
			"threshold": "1",
			"above_below": "above",
			"rule_type": "group",
			"group": group_id,
		}

		self.alerts_collection.remove()
		self.alerts_collection.insert(rule)

		result = self.alerts_collection.count()
		eq_(result, 1)

		self.model.delete_alerts_for_group(group_id)

		result = self.alerts_collection.count()
		eq_(result, 0)


class AlertsModelTest(unittest.TestCase):

	def setUp(self):
		self.model = AlertsModel()
		self.collection = self.model.mongo.get_collection('alerts')
		self.server_collection = self.model.mongo.get_collection('servers')

	def save_alert_test(self):
		self.collection.remove()
		self.model.save({'rule': "test"})
		eq_(self.collection.count(), 1)

	def update_test(self):
		self.collection.remove()
		self.model.save({'rule': "test"})

		alert = self.collection.find_one()
		alert_id = str(alert['_id'])

		self.model.update({'rule': 'updated_test'}, alert_id)

		alert = self.collection.find_one()

		eq_(alert['rule'], 'updated_test')
	

	def mute_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test", "key": "test_me"})
		alert = self.collection.find_one()
		alert_id = str(alert['_id'])

		self.model.mute(alert_id)

		result = self.collection.find_one()
		eq_(result["mute"], True)

		self.model.mute(alert_id)

		result = self.collection.find_one()
		eq_(result["mute"], False)


	def get_server_alerts_test(self):
		self.collection.remove()
		self.server_collection.remove()
		self.server_collection.insert({"name" : "test", "key": "test_me"})
		server = self.server_collection.find_one()
		server_id = str(server['_id'])

		rule = { "server": server_id, "rule_type": 'server', 'metric': 2}
		self.collection.insert(rule)
		
		rule = { "server": server_id, "rule_type": 'server', 'metric': 1}
		self.collection.insert(rule)

		rules = self.model.get_alerts_for_server(type='server', server_id=server_id)

		eq_(len(rules), 2)
		self.collection.remove()


	def get_alerts_test(self):
		self.collection.remove()
		rule = { "server": 'test' , "rule_type": 'bla', 'metric': 2}
		self.collection.insert(rule)

		rules = self.model.get_all_alerts(type='bla')
		eq_(len(rules), 1)
		self.collection.remove()

	def delete_alerts_test(self):
		self.collection.remove()
		self.collection.insert({"name" : "test", "key": "test_me"})
		rule = self.collection.find_one()

		self.model.delete(rule['_id'])

		result = self.collection.count()
		eq_(result,0)


	def save_occurence_test(self):
		self.collection.remove()
		self.collection.insert({"rule_type" : "server",
			"metric_type_value" : "%", 
			"metric_value" : "10", "metric_type" : "more_than", "metric" : "CPU", "threshold": 4})
		
		rule = self.collection.find_one()
		rule_id = str(rule['_id'])

		self.model.save_occurence({'cpu': [{'alert_on': 11, 'rule': rule_id}]})

		rule = self.collection.find_one()
		eq_(len(rule['history']), 1)

		self.model.save_occurence({'cpu': [{'alert_on': 11, 'rule': rule_id}]})
		self.model.save_occurence({'cpu': [{'alert_on': 11, 'rule': rule_id}]})
		
		rule = self.collection.find_one()
		eq_(len(rule['history']), 3)
		
		# Test with unicode
		self.model.save_occurence({'cpu': [{'alert_on': u'22.0', 'rule': rule_id}]})
		rule = self.collection.find_one()
		eq_(len(rule['history']), 4)

		self.collection.remove()

		eq_(rule['history'][3]['trigger'], True)


	def get_all_alerts_test(self):
		self.collection.remove()
		self.collection.insert({"rule_type" : "server"})
		self.collection.insert({"rule_type" : "process"})

		result = self.model.get_all_alerts()
		eq_(len(result), 2)

		self.collection.remove()
	

	def delete_server_alerts_test(self):
		
		self.collection.remove()
		self.collection.insert({"rule_type" : "process", "server": "test-server"})
		self.collection.insert({"rule_type" : "server", "server": "test-server"})
		
		self.collection.insert({"rule_type" : "log", "server": "test-server"})
		self.collection.insert({"rule_type" : "dummy", "server": "test-server"})
		self.collection.insert({"rule_type" : "dummy", "server": "test-server"})

		self.model.delete_server_alerts("test-server")

		eq_(self.collection.count(), 3)
		self.collection.remove()


	def get_by_id_test(self):
		self.collection.remove()
		self.collection.insert({"rule_type" : "process", "server": "test-server"})
		alert = self.collection.find_one()

		alert_from_model = self.model.get_by_id(alert['_id'])
		eq_(alert, alert_from_model)


	def clear_alert_history_test(self):
		self.collection.remove()

		self.collection.insert({"rule_type" : "server",
			"metric_type_value" : "%", 
			"metric_value" : "10", "metric_type" : "more_than", "metric" : "CPU", "threshold": 4})
		
		rule = self.collection.find_one()
		rule_id = str(rule['_id'])

		self.model.save_occurence({'cpu': [{'alert_on': 11, 'rule': rule_id}]})
		self.model.save_occurence({'cpu': [{'alert_on': 11, 'rule': rule_id}]})
		self.model.save_occurence({'cpu': [{'alert_on': 11, 'rule': rule_id}]})

		rule = self.collection.find_one()
		eq_(len(rule['history']), 3)

		self.model.clear_alert_history(rule_id)
		
		rule = self.collection.find_one()
		eq_(len(rule['history']), 0)
		eq_(rule['last_trigger'], 1)
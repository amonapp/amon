from amonone.web.apps.core.basemodel import BaseModel
from amonone.sms.models import sms_recepient_model
from amonone.mail.models import email_recepient_model
from amonone.utils.dates import unix_utc_now


class AlertsModel(BaseModel):

	def __init__(self):
		super(AlertsModel, self).__init__()
		self.collection = self.mongo.get_collection('alerts')


	def save(self, data):
		self.collection.insert(data)
		self.collection.ensure_index([('rule_type', self.desc)])

	def get_by_id(self, alert_id):
		alert_id =  self.mongo.get_object_id(alert_id)
		alert = self.collection.find_one({"_id": alert_id})

		return alert

	def update(self, data, id):
		object_id =  self.mongo.get_object_id(id)

		self.collection.update({"_id": object_id}, {"$set": data}, upsert=True)

	def clear_alert_history(self, alert_id):
		alert_id =  self.mongo.get_object_id(alert_id)
		self.collection.update({"_id": alert_id}, {"$set": {"history": [], "last_trigger": 1}})

	def get_alerts(self, type=None):
		params = {"rule_type": type}
		
		
		rules = self.collection.find(params).count()

		if rules == 0:
			return None
		else:
			rules = self.collection.find(params)

			rules_list = []
			for rule in rules:
				sms_recepients = rule.get('sms_recepients', None)
				if sms_recepients:
					rule['sms_recepients'] = [sms_recepient_model.get_by_id(x) for x in sms_recepients]

				email_recepients = rule.get('email_recepients', None)
				if email_recepients:
					rule['email_recepients'] = [email_recepient_model.get_by_id(x) for x in email_recepients]
				
				rules_list.append(rule)

			return rules_list

	def delete_server_alerts(self):
		rules = self.collection.remove({'$or' : [{'rule_type':'server'}, {'rule_type':'process'}], })

	# Exclude group alerts
	def get_all_alerts(self, type=None):
		
		params = {'$or' : [{'rule_type':'server'}, {'rule_type':'process'}]}
		
		if type != None:
			params = {'$or' : [{'rule_type':type}]}

		count = self.collection.find(params).count()

		if count == 0:
			return None
		else:
			rules = self.collection.find(params)
		
			rules_list = []
			for rule in rules:
				sms_recepients = rule.get('sms_recepients', None)
				if sms_recepients:
					rule['sms_recepients'] = [sms_recepient_model.get_by_id(x) for x in sms_recepients]

				email_recepients = rule.get('email_recepients', None)
				if email_recepients:
					rule['email_recepients'] = [email_recepient_model.get_by_id(x) for x in email_recepients]
				
				rules_list.append(rule)

			return rules_list


	# System and process alerts
	def save_occurence(self, alerts):
		# Format: {'cpu': [{'alert_on': 2.6899999999999977, 'rule': '4f55da92925d75158d0001e0'}}]}
		for key, values_list in alerts.iteritems():
			for value in values_list:
				alert_on = value.get('alert_on', None)
				rule_id = value.get('rule', None)
				metric_type = value.get('metric_type', None)
			
				if alert_on is not None:
					alert_on = "{0:.2f}".format(float(alert_on)) 

				alert = self.get_by_id(rule_id)

				history = alert.get('history', [])
				threshold = alert.get('threshold', 1)
				last_trigger = alert.get('last_trigger', 1)

				trigger = True if int(last_trigger) >= int(threshold) else False
				history.append({"value": alert_on, "time": unix_utc_now(),
				 	"trigger": trigger, "metric_type": metric_type})

				# Reset the last trigger count
				if trigger is True:
					last_trigger = 1
				else:
					last_trigger = last_trigger+1

				alert_id =  self.mongo.get_object_id(rule_id)
				self.collection.update({"_id": alert_id}, {"$set": {"history": history, "last_trigger": last_trigger}})

	
	def mute(self, alert_id):
		alert_id = self.mongo.get_object_id(alert_id)
		result = self.collection.find_one({"_id": alert_id})
		current_mute = result.get('mute', None)

		toggle = False if current_mute is True else True

		self.collection.update({"_id": alert_id}, {"$set": {"mute": toggle}})


alerts_model = AlertsModel()
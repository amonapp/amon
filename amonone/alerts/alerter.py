from copy import deepcopy

from amonone.alerts.system import system_alerts
from amonone.alerts.process import process_alerts
from amonone.mail.sender import send_mail
from amonone.sms.sender import send_sms
from amonone.web.apps.alerts.models import alerts_model
from amonone.web.apps.core.models import server_model
from amonone.log import logging

class ServerAlerter(object):

	def check(self, data=None,  alert_type=None):

		alert_type = 'server' if alert_type == 'server' else 'process'
		
		rules = alerts_model.get_alerts(type=alert_type)

		if rules:
			if alert_type == 'server':
				alerts = system_alerts.check(data, rules)
			elif alert_type == 'process':
				alerts = process_alerts.check(data, rules)
			else:
				alerts = False


			if alerts:
				alerts_model.save_occurence(alerts)
				self.send_alerts()
				
			return alerts # For the test suite


	def send_alerts(self, test=None):
		rules = alerts_model.get_all_alerts()
		alerts = []
		for rule in rules:
			history = rule.get('history', [])
			threshold = rule.get('threshold', 1)
			mute = rule.get('mute', False)

			last_trigger = rule.get('last_trigger', 1)
			trigger = True if int(last_trigger) >= int(threshold) else False

			if trigger is True:
				# Don't append rules for non exisiting servers, check if the alert is muted
				if mute == False:
					alerts.append(rule)

		if len(alerts)> 0:
			# Send emails for each alert
			for alert in alerts: 
				rule_type = alert.get("rule_type", "server") 

				if rule_type == 'process':
					title = "{0}/{1}".format(alert.get('process', ''), alert.get('check',''))
				else:
					title = alert.get('metric', 'System') 
				

				email_recepients = alert.get('email_recepients', [])

				if len(email_recepients) > 0:
					try:
						send_mail(template_data=alert, 
							recepients=email_recepients,
							subject='Amon alert - ({0})'.format(title),
							template='{0}_alert'.format(rule_type)
							)
					except Exception, e:
						logging.exception("Error sending an alert email")
				

				sms_recepients = alert.get('sms_recepients', [])
				
				if len(sms_recepients) > 0:
					try:
						send_sms(alert=alert,
							recepients=sms_recepients,
							template='{0}_alert.txt'.format(rule_type))
					except Exception, e:
						logging.exception("Error sending an alert SMS")

		return None


server_alerter = ServerAlerter()



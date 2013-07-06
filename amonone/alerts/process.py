class ProcessAlerts(object):

	def __init__(self):
		self.alerts = {}

	def check(self, data, rules=None):
		if rules:
			for rule in rules:
				try:
					process_data = data[rule['process']]
				except:
					process_data = False 
					# Can't find the process in the dictionary
	  

				if process_data != False:
					if rule['check'] == 'CPU':
						self.check_cpu(rule, process_data)
					elif rule['check'] == 'Memory':
						self.check_memory(rule, process_data)

			if len(self.alerts) > 0:
				alerts = self.alerts
				self.alerts = {} 
				return alerts
			else:
				return False

		
	def check_memory(self, rule, data):
		alert = False
		process = rule['process']

		if rule['above_below'] == 'above':
			if float(data['memory:mb']) > float(rule['metric_value']):
				alert = True

		if rule['above_below'] == 'below':
			if float(data['memory:mb']) < float(rule['metric_value']):
				alert = True

		if alert:
			alert = {'alert_on': data['memory:mb'], 'rule': str(rule['_id']), 'metric_type': 'MB'}
				
		if alert:
			try:
				len(self.alerts[process])
				self.alerts[process].append(alert)
			except:
				self.alerts[process] = [alert]
			
			return True

	def check_cpu(self, rule, data):
		alert = False
		process = rule['process']
		utilization = float(data['cpu:%'])
		

		if rule['above_below'] == 'above':
			if float(rule['metric_value']) < utilization:
				alert = True

		if rule['above_below'] == 'below':
			if float(rule['metric_value']) > utilization:
				alert = True

		if alert:
			alert = {'alert_on': utilization, 'rule': str(rule['_id']), 'metric_type': '%'}
		
		if alert:
			try:
				len(self.alerts[process])
				self.alerts[process].append(alert)
			except:
				self.alerts[process] = [alert]
			
			return True

process_alerts = ProcessAlerts()

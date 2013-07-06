class SystemAlerts(object):

	def __init__(self):
		self.alerts = {}

	def check(self, data=None, rules=None):
		if rules:
			for rule in rules:
				if rule['metric'] == 'CPU':
					self.check_cpu(rule, data['cpu'])
				elif rule['metric'] == 'Memory':
					self.check_memory(rule, data['memory'])
				elif rule['metric'] == 'Loadavg':
					self.check_loadavg(rule, data['loadavg'])
				elif rule['metric'] == 'Disk':
					self.check_disk(rule, data['disk'])
		
		if len(self.alerts) > 0:
			alerts = self.alerts
			self.alerts = {} 

			return alerts
		else:
			return False
			
		
	def check_memory(self, rule, data):
		last = data.get('last', None)
		if last:
			return False
		alert = False
		# Calculate rules with MB 

		memtotal = float(data['memory:total:mb'])
		memfree = float(data['memory:free:mb'])
		metric_type = rule.get('metric_type')


		if rule['metric_type'] == 'MB':
			used_memory = float(data['memory:used:mb'])
		else:
			used_memory = float(data['memory:used:%'])
		
		if rule['above_below'] == 'above':
			if used_memory > float(rule['metric_value']):
				alert = True

		if rule['above_below'] == 'below':
			if used_memory < float(rule['metric_value']):
				alert = True


		if alert:
			alert = {"alert_on": used_memory , "rule": str(rule['_id']), "metric_type": metric_type}
		if alert:
			try:
				len(self.alerts['memory'])
				self.alerts['memory'].append(alert)
			except:
				self.alerts['memory'] = [alert]
			
			return True 

	def check_cpu(self, rule, data):
		last = data.get('last', None)
		if last:
			return False
		alert = False
		# Utitlization show total cpu usage 
		utilization = float(100)-float(data['idle'])
		
		if rule['above_below'] == 'above':
			if float(rule['metric_value']) < utilization:
				alert = True

		if rule['above_below'] == 'below':
			if float(rule['metric_value']) > utilization:
				alert = True

		if alert:
			alert = {"alert_on": utilization , "rule": str(rule['_id'])}
		
		if alert:
			try:
				len(self.alerts['cpu'])
				self.alerts['cpu'].append(alert)
			except:
				self.alerts['cpu'] = [alert]
			
			return True

	def check_loadavg(self, rule, data):
		last = data.get('last', None)
		if last:
			return False
		alert = False
		value_to_compare = 0
		
		if rule['metric_options'] == 'minute':
			value_to_compare = data['minute']

		if rule['metric_options'] == 'five_minutes':
			value_to_compare = data['five_minutes']

		if rule['metric_options'] == 'fifteen_minutes':
			value_to_compare = data['fifteen_minutes']
		
		value_to_compare = float(value_to_compare)
		
		if rule['above_below'] == 'above':
			if float(rule['metric_value']) < value_to_compare:
				alert = True

		if rule['above_below'] == 'below':
			if float(rule['metric_value']) > value_to_compare:
				alert = True

		if alert:
			alert = {"alert_on": value_to_compare , "rule": str(rule['_id'])}
		
		if alert:
			try:
				len(self.alerts['loadavg'])
				self.alerts['loadavg'].append(alert)
			except:
				self.alerts['loadavg'] = [alert]
			
			return True


	# Internal - checks a single volume
	def _check_volume(self, volume_data, rule, volume):
		alert = False

		used = volume_data['percent'] if rule['metric_type'] == "%" else volume_data['used']
		metric_type = '%' if rule['metric_type'] == '%' else 'MB'
	
		# Convert the data value to MB
		if isinstance(used, str) or isinstance(used, unicode):
			if 'G' in used:
				used = used.replace('G','')
				used = float(used)*1024 
			elif 'MB' in used:
				used = used.replace('MB','')
			elif 'M' in used:
				used = used.replace('M', '')

		
		used= float(used)

		# Convert the rule value to MB if necessary
		if rule['metric_type'] == 'GB':
			metric_value = float(rule['metric_value'])*1024
		else:
			metric_value = float(rule['metric_value'])

		if rule['above_below'] == 'above':
			if metric_value < used:
				alert = True

		if rule['above_below'] == 'below':
			if metric_value > used:
				alert = True

		if alert:
			alert = {"alert_on": used , "rule": str(rule['_id']), 
					 	'metric_type': metric_type,
					 	'volume': volume}
		
		return alert

	def check_disk(self, rule, data):
		last = data.get('last', None)
		
		if last:
			return False
		
		volumes = []
		single_volume = rule.get('metric_options', None)

		if single_volume:
			volumes.append(single_volume)
		else:
			volumes = data.keys()

		if len(volumes) > 0:
			# ["sda1": {'used': '', "free": }]
			for volume in volumes:
				alert = self._check_volume(data[volume], rule, volume)
				disk_alerts = self.alerts.get('disk', [])

				if len(disk_alerts) == 0:
					self.alerts['disk'] = [alert]
				else:
					self.alerts['disk'].append(alert)
	
			return True

	

system_alerts = SystemAlerts()

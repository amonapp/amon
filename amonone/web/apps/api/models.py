from amonone.web.apps.core.basemodel import BaseModel
from amonone.utils.dates import unix_utc_now
from amonone.alerts.alerter import server_alerter

class ApiModel(BaseModel):

	def __init__(self):
		super(ApiModel, self).__init__()

		self.server_collection = self.mongo.get_collection('server')
		self.server = self.server_collection.find_one()

		if self.server is None:
			self.server_collection.insert({})

			self.server =  self.server_collection.find_one()


	def server_update_disk_volumes(self, volumes):
		try:
			volume_data = volumes.keys()
		except:
			volume_data = False

		if volume_data:
			valid_volumes = filter(lambda x: x not in ['time','last'], volume_data)
			
			self.server_collection.update({"_id": self.server['_id']}, {"$set": {"volumes": valid_volumes}})

	
	def server_update_network_interfaces(self,  interfaces):
		try:
			interfaces_data = interfaces.keys()
		except:
			interfaces_data = False
	   
		if interfaces_data:
			valid_adapters = filter(lambda x: x not in ['time','last','lo'], interfaces_data)
			
			self.server_collection.update({"_id": self.server['_id']}, {"$set": {"network_interfaces": valid_adapters}})

	def server_update_last_check(self,  last_check):
		self.server_collection.update({"_id": self.server['_id']}, {"$set": {"last_check": last_check}})


	def server_update_processes(self, processes):
		existing_processes =  self.server.get('processes', [])
		updated_list =  list(set(existing_processes).union(processes))
		
		cleaned_list = []
		for element in updated_list:
			if element.find("/") ==-1:
				cleaned_list.append(element)

		self.server_collection.update({"_id": self.server['_id']},  {"$set": {"processes": cleaned_list}})


	def store_system_entries(self, data):

			data["time"] = unix_utc_now()

			self.server_update_disk_volumes(data.get('disk', None))
			self.server_update_network_interfaces(data.get('network', None))
			self.server_update_last_check(data['time'])
			
						
			collection = self.mongo.get_collection('system')
			collection.insert(data)
			collection.ensure_index([('time', self.desc)])

			# Check for alerts
			server_alerter.check(data=data, alert_type='server')
		

	def store_process_entries(self, data):
			
		
		self.server_update_processes(data.keys())

		collection = self.mongo.get_collection('processes')
		data["time"] = unix_utc_now()
		collection.insert(data)
		collection.ensure_index([('time', self.desc)])

		# Check for alerts
		server_alerter.check(data=data, alert_type='process')


api_model = ApiModel()

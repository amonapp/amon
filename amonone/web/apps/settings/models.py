from amonone.web.apps.core.basemodel import BaseModel
from amonone.web.utils import generate_api_key
from amonone.utils.dates import unix_utc_now
from amonone.web.apps.core.models import server_model


class DataModel(BaseModel):

	def __init__(self):
		super(DataModel, self).__init__()
		
		self.protected_collections = ['system.indexes', 'users', 
				'sessions','tags','servers',
				'unread', 'alerts', 'email_settings', 'sms_settings']
		

	def get_database_info(self):
		return self.db.command('dbstats')


	def get_server_collection_stats(self):
		all_servers = server_model.get_all()
		data = {}
		if all_servers:
			for server in all_servers:
				system_collection = self.mongo.get_server_system_collection(server)
				process_collection = self.mongo.get_server_processes_collection(server)

				system_info = self.get_collection_stats(system_collection.name)
				process_info = self.get_collection_stats(process_collection.name)

				data[server['name']] = {"system_info": system_info, 
									"process_info": process_info,
									"server_id": server['_id']
								}

		return data


	def get_collection_stats(self, collection):
		try:
			stats = self.db.command('collstats', collection)
		except:
			stats = None
		
		return stats

	def cleanup_system_collection(self, server, date):
		collection = self.mongo.get_server_system_collection(server)

		params = {}
		if date != None:
			params['time'] = {"$lte": date }

			collection.remove(params)

	def cleanup_process_collection(self, server, date):
		collection = self.mongo.get_server_processes_collection(server)

		params = {}
		if date != None:
			params['time'] = {"$lte": date }

			collection.remove(params)


	def delete_system_collection(self, server):
		system_collection = self.mongo.get_server_system_collection(server)
		self.db.drop_collection(system_collection)

	def delete_process_collection(self, server):
		process_collection = self.mongo.get_server_processes_collection(server)
		self.db.drop_collection(process_collection)


data_model = DataModel()

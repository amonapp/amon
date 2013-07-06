from amonone.web.apps.core.basemodel import BaseModel

class ProcessModel(BaseModel):

	def __init__(self):
		super(ProcessModel, self).__init__()

	def get_process_data(self, processes, date_from, date_to,):

		collection = self.mongo.get_collection('processes')

		data = collection.find({"time": {"$gte": date_from,"$lte": date_to }}).sort('time', self.desc)

		filtered_data = {}
		# Create the base structure
		for process in processes:
			filtered_data[process] = {"memory": {}, "cpu": {}}

		for line in data:
			time = line['time']

			for process in processes:
				try:
					process_data = line.get(process, None)
					memory = process_data.get("memory:mb", 0)
					cpu = process_data.get("cpu:%", 0)
				except:
					memory = 0
					cpu = 0
				
				try:
					filtered_data[process]["memory"][time] = memory
					filtered_data[process]["cpu"][time] = cpu
				except:
					pass
				
		return filtered_data


process_model = ProcessModel()
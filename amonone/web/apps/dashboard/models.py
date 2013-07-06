from amonone.web.apps.core.basemodel import BaseModel


class DashboardModel(BaseModel):

	def __init__(self):
		super(DashboardModel, self).__init__()

	def build_process_dict(self, process_check):
		cpu_list = []
		memory_list = []

		for process, values in process_check.iteritems():
			if isinstance(values, dict):
				process_cpu = values.get('cpu:%', 0)
				process_memory = values.get('memory:mb', 0)

				cpu_list.append(float(process_cpu))
				memory_list.append(float(process_memory))

		processes_data = {
			'details': process_check,
			'total_memory_usage':  sum(memory_list),
			'total_cpu_usage': sum(cpu_list)
		}

		return processes_data

	def get_system_check(self, date):
		system_check = {}

		collection = self.mongo.get_collection('system')

		params = {}
		sort = self.desc
		if date:
			params = {"time": {"$gte": date}}
			sort= self.asc
	
		try:
			system_check = collection.find(params, sort=[("time", sort)]).limit(1)[0]
		except IndexError:
			pass

		return system_check


	def get_process_check(self, date):
		processes_data = None
		collection = self.mongo.get_collection('processes')			
			
		params = {}
		sort = self.desc
		if date:
			params = {"time": {"$gte": date}}
			sort= self.asc

		try:
			process_check = collection.find(params, sort=[("time", sort)]).limit(1)[0]
		except IndexError:
			process_check = False

		if process_check:
			processes_data = self.build_process_dict(process_check)
	
		return processes_data

dashboard_model = DashboardModel()
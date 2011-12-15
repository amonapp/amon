from amon.backends.mongodb import MongoBackend
from pymongo import DESCENDING, ASCENDING 
from hashlib import sha1

class BaseModel(object):

	def __init__(self):
		self.mongo = MongoBackend()
		

class DashboardModel(BaseModel):
	
	def __init__(self):
		super(DashboardModel, self).__init__()

	def get_last_system_check(self, active_system_checks):
		last_check = {}
		
		try:
			for check in active_system_checks:
				row = self.mongo.get_collection(check)
				# don't break the dashboard if the daemon is stopped
				last_check[check] = row.find({"last":{"$exists" : False}},limit=1).sort('time', DESCENDING)[0]
		except Exception, e:
			last_check = False
			raise e

		return last_check

	def get_last_process_check(self, active_process_checks):
		process_check = {}

		try:
			for check in active_process_checks:
				row = self.mongo.get_collection(check)
				process_check[check] = row.find({"last":{"$exists" : False}}, limit=1).sort('time', DESCENDING)[0]
		except Exception, e:
			process_check = False

		return process_check



class SystemModel(BaseModel):

	def __init__(self):
		super(SystemModel, self).__init__()

	"""
	Return pymongo object every active check
	Example: 
		active_checks = ['cpu'] will get everything in the collection amon_cpu, between date_from and date_to
	"""
	def get_system_data(self, active_checks, date_from, date_to):
		
		checks = {}

		try:
			for check in active_checks:
				row = self.mongo.get_collection(check)
				checks[check] = row.find({"time": {"$gte": date_from,"$lte": date_to }}).sort('time', ASCENDING)
		except Exception, e:
			checks = False

		return checks

	"""
	Used in the Javascript calendar - doesn't permit checks for dates before this date
	"""
	def get_first_check_date(self):
		try:
			row = self.mongo.get_collection('cpu')
			start_date = row.find_one()
		except Exception, e:
			start_date = False

		return start_date


	
class ProcessModel(BaseModel):
	
	def __init__(self):
		super(ProcessModel, self).__init__()

	def get_process_data(self, active_checks, date_from, date_to):
		
		process_data = {}
		for process in active_checks:
			row = self.mongo.get_collection(process)
			cursor = row.find({"time": {"$gte": date_from, '$lte': date_to}}).sort('time', ASCENDING) 
			
			process_data[process] = cursor

		return process_data


class ExceptionModel(BaseModel):
	
	def __init__(self):
		super(ExceptionModel, self).__init__()
		self.row = self.mongo.get_collection('exceptions') 

	def get_exceptions(self):
		exceptions = self.row.find().sort('last_occurrence', DESCENDING)

		return exceptions

	def mark_as_read(self):
		unread_collection = self.mongo.get_collection('unread')
		unread_collection.update({"id": 1}, {"$set": {"exceptions": 0}})


class LogModel(BaseModel):
	
	def __init__(self):
		super(LogModel, self).__init__()
		self.row = self.mongo.get_collection('logs') 

	def get_logs(self):
		logs = self.row.find().sort('time', DESCENDING)

		return logs

	def filtered_logs(self, level, filter):

		query = {}
		if level:
			level_params = [{'level': x} for x in level]
			query = {"$or" : level_params}

		if filter:
			query['_searchable'] = { "$regex": str(filter), "$options": 'i'}

		logs = self.row.find(query).sort('time', DESCENDING)

		return logs

	def mark_as_read(self):
		unread_collection = self.mongo.get_collection('unread')
		unread_collection.update({"id": 1}, {"$set": {"logs": 0}})


class CommonModel(BaseModel):

	def __init__(self):
		super(CommonModel, self).__init__()


	def get_unread_values(self):
		unread_collection = self.mongo.get_collection('unread')
		unread_values = unread_collection.find_one()

		return unread_values


class UserModel(BaseModel):
	
	def __init__(self):
		super(UserModel, self).__init__()
		self.collection = self.mongo.get_collection('users')


	def create_user(self, userdata):
		userdata['password'] = sha1(userdata['password']).hexdigest()
		self.collection.save(userdata)

	def check_user(self, userdata):
		userdata['password'] = sha1(userdata['password']).hexdigest()
		result = self.collection.find_one({"username": userdata['username'],
									"password": userdata['password']})


		return result if result else {}

	
	def count_users(self):
		 return self.collection.count()	

	def username_exists(self, username):
		result = self.collection.find({"username": username}).count()

		return result


dashboard_model = DashboardModel()
common_model = CommonModel()
process_model = ProcessModel()
system_model = SystemModel()
exception_model = ExceptionModel()
log_model = LogModel()
user_model = UserModel()

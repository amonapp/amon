import redis

class RedisBackend(object):
	
	def __init__(self):
		self.r = redis.Redis(host='localhost', port=6379, db=0) #TODO get this values from a config file	


	def save_dict(self, dict):
		"""
		 Save a python dictionary to Redis sorted set
		
		"""
		session_time = dict['time']
		self.r.zadd('amon_log', dict, session_time)

from check import AmonCheckSystem
from time import time

class AmonRunner(object):
	
	def __init__(self):
		pass

	def run(self):
		

		_syscheck = AmonCheckSystem()
		log_dict = {}
		
		now = int(time())
		
		log_dict['time'] = now

		memory = _syscheck.get_memory_info()

		if memory != False:
			log_dict['memory'] = memory

		
		cpu = _syscheck.get_cpu_utilization()

		if cpu != False:
			log_dict['cpu'] = cpu
		


		return log_dict
			


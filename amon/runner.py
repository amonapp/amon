from check import System
from time import time

class Runner(object):
	
	def __init__(self):
		pass

	def run(self):
		

		_syscheck = System()
		log_dict = {}
		
		now = int(time())
		
		log_dict['time'] = now


		memory = _syscheck.get_memory_info()

		if memory != False:
			log_dict['memory'] = memory

		
		cpu = _syscheck.get_cpu_utilization()

		if cpu != False:
			log_dict['cpu'] = cpu
		

		loadavg = _syscheck.get_load_average()

		if loadavg != False:
			log_dict['loadavg'] = loadavg


		disk = _syscheck.get_disk_usage()

		if disk != False:
			log_dict['disk'] = disk

		network = _syscheck.get_network_traffic()

		if network != False:
			log_dict['network'] = network

		return log_dict
			


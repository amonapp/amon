from amon.system.check import system_info_collector
from amon.core import settings
from time import time

class Runner(object):
	
	def __init__(self):
		self.active_checks = settings.ACTIVE_CHECKS

	def run(self):
		
		system_info_dict = {}
		
		now = int(time()) # unix time
		
		if 'memory' in self.active_checks:
			memory = system_info_collector.get_memory_info()

			if memory != False:
				memory['time'] = now
				system_info_dict['memory'] = memory

		
		if 'cpu' in self.active_checks:
			cpu = system_info_collector.get_cpu_utilization()

			if cpu != False:
				cpu['time'] = now
				system_info_dict['cpu'] = cpu
		

		if 'loadavg' in self.active_checks:
			loadavg = system_info_collector.get_load_average()

			if loadavg != False:
				loadavg['time'] = now
				system_info_dict['loadavg'] = loadavg


		if 'disk' in self.active_checks:
			disk = system_info_collector.get_disk_usage()

			if disk != False:
				disk['time'] = now
				system_info_dict['disk'] = disk

		if 'network' in self.active_checks:
			network = system_info_collector.get_network_traffic()

			if network != False:
				network['time'] = now
				system_info_dict['network'] = network

		return system_info_dict

	# empty dictionary, used when stopping the daemon to avoid chart bugs
	def last(self):
		empty_dict = {}
		now = int(time())
		for check in self.active_checks:
			empty_dict[check] = {'time': now, 'last': 1}

		return empty_dict

runner = Runner()
			


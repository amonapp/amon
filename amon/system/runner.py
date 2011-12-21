from amon.system.collector import system_info_collector, process_info_collector
from amon.core import settings
from time import time
import sys

class Runner(object):
	
	def __init__(self):
		self.active_checks = settings.SYSTEM_CHECKS
		self.process_checks = settings.PROCESS_CHECKS

	def system(self):
		
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

		if 'network' in self.active_checks and sys.platform != 'darwin':
			network = system_info_collector.get_network_traffic()

			if network != False:
				network['time'] = now
				system_info_dict['network'] = network

		return system_info_dict

	# empty dictionary, used when stopping the daemon to avoid chart bugs
	def empty(self):
		empty_dict = {}
		now = int(time())
		for check in self.active_checks:
			empty_dict[check] = {'time': now, 'last': 1}

		return empty_dict

	def processes(self):
		now = int(time()) # unix time

		process_info_dict = {}
		for process in self.process_checks:
			process_info_dict[process]  = process_info_collector.check_process(process)
			process_info_dict[process]['time'] = now

		return process_info_dict

runner = Runner()
			


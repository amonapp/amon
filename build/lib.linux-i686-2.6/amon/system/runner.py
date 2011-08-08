from amon.system.check import system_info_collector
from time import time

class Runner(object):
	
	def __init__(self):
		pass

	def run(self):
		
		system_info_dict = {}
		
		now = int(time()) # unix time
		
		memory = system_info_collector.get_memory_info()

		if memory != False:
			memory['time'] = now
			system_info_dict['memory'] = memory

		
		cpu = system_info_collector.get_cpu_utilization()

		if cpu != False:
			cpu['time'] = now
			system_info_dict['cpu'] = cpu
		

		loadavg = system_info_collector.get_load_average()

		if loadavg != False:
			loadavg['time'] = now
			system_info_dict['loadavg'] = loadavg


		disk = system_info_collector.get_disk_usage()

		if disk != False:
			disk['time'] = now
			system_info_dict['disk'] = disk

		network = system_info_collector.get_network_traffic()

		if network != False:
			network['time'] = now
			system_info_dict['network'] = network

		return system_info_dict


runner = Runner()
			


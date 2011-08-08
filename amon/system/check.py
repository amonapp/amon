import os
import re
import subprocess

class SystemInfoCollector(object):

	def __init__(self):
		pass
	
	def get_memory_info(self):
		
		regex = re.compile(r'([0-9]+)')

		mem_dict = {}
		
		with open('/proc/meminfo', 'r') as lines:
			
			_save_to_dict = ['MemFree', 'MemTotal', 'SwapFree', 'SwapTotal']
			
			for line in lines:
				values = line.split(':')	
				
				match = re.search(regex, values[1])
				if values[0] in _save_to_dict:
					mem_dict[values[0].lower()] = int(match.group(0)) / 1024
			
			return mem_dict


	def get_disk_usage(self):
		df = subprocess.Popen(['df','-h'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]	
		
		volumes = df.split('\n')	
		volumes.pop(0)	# remove the header
		volumes.pop()

		data = {}

		_columns = ('volume', 'total', 'used', 'free', 'percent', 'path')	
		
		for volume in volumes:
			line = volume.split()
			if line[0].startswith('/'):
				_volume = dict(zip(_columns, line))

				# strip /dev/
				_name = _volume['volume'].replace('/dev/', '')
				data[_name] = _volume

		return data
				
		
	def get_uptime(self):

		with open('/proc/uptime', 'r') as line:
			contents = line.read().split()
 
		total_seconds = float(contents[0])
 
		MINUTE  = 60
		HOUR    = MINUTE * 60
		DAY     = HOUR * 24

		days    = int( total_seconds / DAY )
		hours   = int( ( total_seconds % DAY ) / HOUR )
		minutes = int( ( total_seconds % HOUR ) / MINUTE )
		seconds = int( total_seconds % MINUTE )
	 
		uptime = "{0} days {1} hours {2} minutes {3} seconds".format(days, hours, minutes, seconds)

		return uptime



	def get_network_traffic(self):
		
		lines = open("/proc/net/dev", "r").readlines()

		columnLine = lines[1]
		_, receiveCols , transmitCols = columnLine.split("|")
		receiveCols = map(lambda a:"recv_"+a, receiveCols.split())
		transmitCols = map(lambda a:"trans_"+a, transmitCols.split())

		cols = receiveCols+transmitCols

		faces = {}

		for line in lines[2:]:
			if line.find(":") < 0: continue
			face, data = line.split(":")
			faceData = dict(zip(cols, data.split()))
			faces[face.strip()] = faceData

		return faces


	def get_load_average(self):
		lines = open('/proc/loadavg','r').readlines()

		load_data = lines[0].split()

		_loadavg_columns = ['minute','five_minutes','fifteen_minutes','scheduled_processes']
		_loadavg_values = load_data[:4]
		
		load_dict = dict(zip(_loadavg_columns, _loadavg_values))	
		
		return load_dict 
		

	def get_cpu_utilization(self):
		vmstat = subprocess.Popen(['vmstat'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]	
		
		lines = vmstat.splitlines()
		raw_data = lines[2].split()

		_cpu_columns  = ['user', 'system','idle', 'wait']
		_cpu_values = map(int, raw_data[-4:]) 

		cpu_dict = dict(zip(_cpu_columns, _cpu_values))

		return cpu_dict
		
	
system_info_collector = SystemInfoCollector()

# WORK IN PROGRESS
class ProcessInfoCollector(object):

	def __init__(self):
		pass

	def check_process_by_name(self, name=None):

		ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, close_fds=True)
		grep = subprocess.Popen(['grep', 'redis'],stdin=ps.stdout,  stdout=subprocess.PIPE, close_fds=True).communicate()[0]
	
	
	
	def _pid_list(self):
		return [int(x) for x in os.listdir('/proc') if x.isdigit()] 




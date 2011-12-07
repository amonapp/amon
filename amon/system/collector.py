import os
import re
import subprocess
import sys

class SystemInfoCollector(object):

	def __init__(self):
		pass
	
	def get_macos_stats(self):
		'''
		Some stats on MacOS doesn't work the same way as in Linux. 
		This function returns the values for these exceptions
		'''

		stats_dict = {}

		stats = subprocess.Popen(['top','-F','-R','-l','1'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]	
		lines = stats.splitlines()
		lines = lines[0:10]
		for line in lines:

			if line.startswith('PhysMem'):
				
				memory = line.split(',')
				memory_values = map(lambda x: int(re.findall(r'\d+', x)[0]), memory)
				memtotal = memory_values[-2]+memory_values[-1]
				stats_dict['memory'] = {'memfree' : memory_values[-2], 'memtotal': memtotal, 'swapfree': 0, 'swaptotal': 0}

			if line.startswith('Load'):
				
				load = line.split(',')
				load_values = map(lambda x: re.findall(r'\d+.\d+', x)[0], load)
				load_values.append(0) # scheduled_processes 
				load_values = map(lambda x: str(x), load_values) # convert the values to strings. WORKARROUND
				stats_dict['loadavg'] = load_values

			if line.startswith('CPU'):
				
				cpu = line.split(',')
				cpu_values = map(lambda x: re.findall(r'\d+.\d+', x)[0], cpu)
				cpu_values = map(lambda x: int(float(x)), cpu_values) # convert the values to int
				cpu_columns = ['user','system', 'idle']
				stats_dict['cpu'] = dict(zip(cpu_columns, cpu_values))
				
		return	stats_dict

	def get_memory_info(self):
		
		mem_dict = {}
		_save_to_dict = ['MemFree', 'MemTotal', 'SwapFree', 'SwapTotal']
		
		if sys.platform == 'darwin':
			mem_dict = self.get_macos_stats()['memory']
			return mem_dict

		regex = re.compile(r'([0-9]+)')

		
		with open('/proc/meminfo', 'r') as lines:
			
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

		previous_line = None
		
		for volume in volumes:
			line = volume.split(None, 6)

			if len(line) == 1: # If the length is 1 then this just has the mount name
				previous_line = line[0] # We store it, then continue the for
				continue

			if previous_line != None: 
				line.insert(0, previous_line) # then we need to insert it into the volume
				previous_line = None # reset the line

			if line[0].startswith('/'):
				_volume = dict(zip(_columns, line))

				# strip /dev/
				_name = _volume['volume'].replace('/dev/', '')
				
				# Encrypted directories -> /home/something/.Private
				if '.' in _name:
					_name = _name.replace('.','')
				
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

		if sys.platform == 'darwin':
			return False
		
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
		_loadavg_columns = ['minute','five_minutes','fifteen_minutes','scheduled_processes']
		
		if sys.platform == 'darwin':
			loadavg = self.get_macos_stats()['loadavg']
			load_dict = dict(zip(_loadavg_columns, loadavg))
			
			return load_dict

		lines = open('/proc/loadavg','r').readlines()

		load_data = lines[0].split()

		_loadavg_values = load_data[:4]
		
		load_dict = dict(zip(_loadavg_columns, _loadavg_values))	
		
		return load_dict 
		

	def get_cpu_utilization(self):
		if sys.platform == 'darwin':
			cpu_dict = self.get_macos_stats()['cpu']
			return cpu_dict

		# Get only the cpu stats
		mpstat = subprocess.Popen(['iostat', '-c'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
				
		cpu_columns = []
		cpu_values = []
		header_regex = re.compile(r'.*?([%][a-zA-Z0-9]+)[\s+]?') # the header values are %idle, %wait
		# International float numbers - could be 0.00 or 0,00
		value_regex = re.compile(r'\d+[\.,]\d+') 
		stats = mpstat.split('\n')


		for value in stats:
			values = re.findall(value_regex, value)
			if len(values) > 4:
				cpu_values = map(lambda x: int(float(x)), values) # Convert the values to float and then to int

			header = re.findall(header_regex, value)
			if len(header) > 4:
				cpu_columns = map(lambda x: x.replace('%', ''), header) 

		cpu_dict = dict(zip(cpu_columns, cpu_values))

		return cpu_dict
		
	
system_info_collector = SystemInfoCollector()

class ProcessInfoCollector(object):

	def __init__(self):
		memory = system_info_collector.get_memory_info()
		self.total_memory = memory['memtotal']

	def check_process(self, name=None):
		# get the process info, remove grep from the result, print cpu, memory
		# ps aux |grep 'postgres' | grep -v grep | awk '{print $3","$4}' 

		ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, close_fds=True)
		grep = subprocess.Popen(['grep', str(name)], stdin=ps.stdout, stdout=subprocess.PIPE, close_fds=True)
		remove_grep = subprocess.Popen(['grep', '-v','grep'], stdin=grep.stdout, stdout=subprocess.PIPE, close_fds=True)
		awk = subprocess.Popen(['awk', '{print $3","$4}'], stdin=remove_grep.stdout,\
		stdout=subprocess.PIPE, close_fds=True).communicate()[0]	

		lines = [0,0]
		for line in awk.splitlines():
			cpu_memory = line.split(',')
			cpu_memory = map(lambda x:  float(x), cpu_memory)
			lines[0] = lines[0]+cpu_memory[0]
			lines[1] = lines[1]+cpu_memory[1]
		lines  = map(lambda x:  "{0:.2f}".format(x), lines)
		
		cpu, memory = lines[0], lines[1]

		process_memory_mb = float(self.total_memory/100) * float(memory) # Convert the % in MB
		memory = "{0:.3}".format(process_memory_mb)
		process_info = {'cpu': cpu, 'memory': memory}
		
		return process_info
	
	

process_info_collector = ProcessInfoCollector()


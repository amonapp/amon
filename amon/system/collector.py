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
		# Get only the cpu stats
		mpstat = subprocess.Popen(['iostat', '-c'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]
				
		cpu_columns = []
		cpu_values = []
		header_regex = re.compile(r'.*?([%][a-zA-Z0-9]+)[\s+]?') # the header values are %idle, %wait
		value_regex = re.compile(r'\d+\.\d+') # values are 0.00
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
		# ps aux columns 
		# USER PID  %CPU %MEM  VSZ RSS TTY STAT START TIME COMMAND 
		ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, close_fds=True)
		grep = subprocess.Popen(['grep', name],stdin=ps.stdout,  stdout=subprocess.PIPE, close_fds=True).communicate()[0]
		
		stats = grep.split()
		user, pid, cpu, memory = stats[0], stats[1], stats[2], stats[3]

		process_memory_mb = float(self.total_memory/100) * float(memory) # Convert the % in MB
		memory = "{0:.3}".format(process_memory_mb)
		process_info = {'user': user, 'pid': pid, 'cpu': cpu, 'memory': memory}
		
		return process_info
	
	
	def _pid_list(self):
		return [int(x) for x in os.listdir('/proc') if x.isdigit()] 


process_info_collector = ProcessInfoCollector()


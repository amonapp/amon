import subprocess
import sys
import re
import os
import glob

from amonone.core.collector.utils import split_and_slugify

class SystemCollector(object):


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

	def get_system_info(self):
		distro_info_file = glob.glob('/etc/*-release')
		debian_version = glob.glob('/etc/debian_version')

		debian = False
		distro_info = None
		try: 
			distro_info = subprocess.Popen(["cat"] + distro_info_file, stdout=subprocess.PIPE, close_fds=True,
				).communicate()[0]
		except:
			distro_info = subprocess.Popen(["cat"] + debian_version, stdout=subprocess.PIPE, close_fds=True,
				).communicate()[0]
			debian = True

		system_info = {}
		distro = {}
		if debian is False:
			for line in distro_info.splitlines():
				if re.search('distrib_id', line, re.IGNORECASE):
					info = line.split("=")
					if len(info) == 2:
						distro['distribution'] = info[1]
				if re.search('distrib_release', line, re.IGNORECASE):
					info = line.split("=")
					if len(info) == 2:
						distro['release'] = info[1]
		else:
			distro['distribution'] = 'Debian'
			distro['release'] = distro_info
		
		system_info["distro"] = distro

		processor_info = subprocess.Popen(["cat", '/proc/cpuinfo'], stdout=subprocess.PIPE, close_fds=True,
			).communicate()[0]

		processor = {}
		for line in processor_info.splitlines():
			parsed_line = split_and_slugify(line)
			if parsed_line and isinstance(parsed_line, dict):
				key = parsed_line.keys()[0]
				value = parsed_line.values()[0]
				processor[key] = value

		system_info["processor"] = processor
		  
		return system_info

	def get_memory_info(self):

		memory_dict = {}
		_save_to_dict = ['MemFree', 'MemTotal', 'SwapFree', 'SwapTotal', 'Buffers', 'Cached']

		regex = re.compile(r'([0-9]+)')

		with open('/proc/meminfo', 'r') as lines:

			for line in lines:
				values = line.split(':')
			
				match = re.search(regex, values[1])
				if values[0] in _save_to_dict:
					memory_dict[values[0].lower()] = int(match.group(0)) / 1024 # Convert to MB

			# Unix releases buffers and cached when needed
			buffers = memory_dict.get('buffers', 0)
			cached = memory_dict.get('cached', 0)

			memory_free = memory_dict['memfree']+buffers+cached
			memory_used = memory_dict['memtotal']-memory_free
			memory_percent_used = (float(memory_used)/float(memory_dict['memtotal'])*100)
			
			swap_total = memory_dict.get('swaptotal', 0)
			swap_free = memory_dict.get('swapfree', 0)
			swap_used = swap_total-swap_free
			swap_percent_used = 0
			
			if swap_total > 0:
				swap_percent_used = (float(swap_used)/float(swap_total) * 100)

			extracted_data = {
				"memory:total:mb": memory_dict["memtotal"],
				"memory:free:mb": memory_free,
				"memory:used:mb": memory_used,
				"memory:used:%": memory_percent_used,
				"swap:total:mb":swap_total,
				"swap:free:mb": swap_free,
				"swap:used:mb": swap_used,
				"swap:used:%": swap_percent_used
			}

			# Convert everything to int to avoid float localization problems
			for k,v in extracted_data.items():
				extracted_data[k] = int(v)
		   
			return extracted_data


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

				_volume['percent'] = _volume['percent'].replace("%",'') # Delete the % sign for easier calculation later

				# strip /dev/
				_name = _volume['volume'].replace('/dev/', '')

				# Encrypted directories -> /home/something/.Private
				if '.' in _name:
					_name = _name.replace('.','')

				data[_name] = _volume

		return data



	def get_network_traffic(self):

		stats = subprocess.Popen(['sar','-n','DEV','1','1'], 
			stdout=subprocess.PIPE, close_fds=True)\
				.communicate()[0]
		network_data = stats.splitlines()
		data = {}
		for line in network_data:
			if line.startswith('Average'):
				elements = line.split()
				interface = elements[1]
				
				# interface name with . 
				if '.' in interface:
					interface = interface.replace('.','-')

				if interface not in ['IFACE', 'lo']:
					# rxkB/s - Total number of kilobytes received per second  
					# txkB/s - Total number of kilobytes transmitted per second
					
					kb_received = elements[4].replace(',', '.')
					kb_received = format(float(kb_received), ".2f")

					kb_transmitted = elements[5].replace(',', '.')
					kb_transmitted = format(float(kb_transmitted), ".2f")

					data[interface] = {"kb_received": kb_received , "kb_transmitted": kb_transmitted}

		return data

	 
	def get_load_average(self):
		_loadavg_columns = ['minute','five_minutes','fifteen_minutes','scheduled_processes']


		lines = open('/proc/loadavg','r').readlines()

		load_data = lines[0].split()

		_loadavg_values = load_data[:4]

		load_dict = dict(zip(_loadavg_columns, _loadavg_values))	


		# Get cpu cores 
		cpuinfo = subprocess.Popen(['cat', '/proc/cpuinfo'], stdout=subprocess.PIPE, close_fds=True)
		grep = subprocess.Popen(['grep', 'cores'], stdin=cpuinfo.stdout, stdout=subprocess.PIPE, close_fds=True)
		sort = subprocess.Popen(['sort', '-u'], stdin=grep.stdout, stdout=subprocess.PIPE, close_fds=True)\
				.communicate()[0]

		cores = re.findall(r'\d+', sort) 

		try:
			load_dict['cores'] = int(cores[0])
		except:
			load_dict['cores'] = 1 # Don't break if can't detect the cores 

		return load_dict 


	def get_cpu_utilization(self):

		# Get the cpu stats
		mpstat = subprocess.Popen(['sar', '1','1'], 
			stdout=subprocess.PIPE, close_fds=True).communicate()[0]

		cpu_columns = []
		cpu_values = []
		header_regex = re.compile(r'.*?([%][a-zA-Z0-9]+)[\s+]?') # the header values are %idle, %wait
		# International float numbers - could be 0.00 or 0,00
		value_regex = re.compile(r'\d+[\.,]\d+') 
		stats = mpstat.split('\n')

		for value in stats:
			values = re.findall(value_regex, value)
			if len(values) > 4:
				values = map(lambda x: x.replace(',','.'), values) # Replace , with . if necessary
				cpu_values = map(lambda x: format(float(x), ".2f"), values) # Convert the values to float with 2 points precision

			header = re.findall(header_regex, value)
			if len(header) > 4:
				cpu_columns = map(lambda x: x.replace('%', ''), header) 

		cpu_dict = dict(zip(cpu_columns, cpu_values))
		
		return cpu_dict

system_info_collector = SystemCollector()


class ProcessInfoCollector(object):

	def __init__(self):
		memory = system_info_collector.get_memory_info()
		self.total_memory = memory['memory:total:mb']

	def process_list(self):
		stats = subprocess.Popen(['pidstat','-ruht'], 
			stdout=subprocess.PIPE, close_fds=True)\
				.communicate()[0]

		stats_data = stats.splitlines()
		del stats_data[0:2] # Deletes Unix system data

		converted_data = []
		for line in stats_data:
			if re.search('command', line, re.IGNORECASE): # Matches the first line
				header = line.split()
				del header[0] # Deletes the # symbol
			else:
				command = line.split()
				data_dict = dict(zip(header, command))
				
				process_memory_mb = float(self.total_memory/100) * float(data_dict["%MEM"].replace(",",".")) # Convert the % in MB
				memory = "{0:.3}".format(process_memory_mb)
				memory = memory.replace(",", ".")

				cpu = "{0:.2f}".format(float(data_dict["%CPU"].replace(",",".")))
				cpu = cpu.replace(",", ".")
				
				command = data_dict["Command"]

				if not re.search('_', command, re.IGNORECASE):
					extracted_data = {"cpu:%": cpu,
								  "memory:mb": memory,
								  "command": command}
					converted_data.append(extracted_data)

		return converted_data
	
process_info_collector = ProcessInfoCollector()

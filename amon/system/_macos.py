import subprocess
import re

class MacOSSystemCollector(object):

	def get_load_average(self):
		loadavg_columns = ['minute','five_minutes','fifteen_minutes','cores']
		
		load = subprocess.Popen(['sysctl','vm.loadavg'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]	
		load_values = re.findall(r'\d+.\d+', load)


		cores = subprocess.Popen(['sysctl','-n','hw.logicalcpu'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]	
		load_values.append(int(cores))

		loadavg = dict(zip(loadavg_columns, load_values))
		
		return loadavg

	def get_cpu_utilization(self):
		cpu = subprocess.Popen(['iostat'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]	
		lines = cpu.splitlines()
		lines.pop(0)
		header = lines[0].split()
		values = lines[1].split()
		values_dict = dict(zip(header, values))

		cpu_columns = {"user": int(values_dict['us']),
					   "idle": int(values_dict['id']),
					   "system": int(values_dict['sy'])}

		return cpu_columns

	def get_memory_info(self):
		memory_dict = {'memfree': 0, 'memtotal': 0, 'swapfree': 0, 'swaptotal': 0}
		
		memory_total = subprocess.Popen(['sysctl','-n','hw.memsize'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]	
		memory_dict['memtotal'] = int(memory_total)/1024/1024
		
		# Get process info
		vm = subprocess.Popen(['vm_stat'], stdout=subprocess.PIPE).communicate()[0]

		# Process vm_stat
		vmLines = vm.splitlines()
		del vmLines[0] # Delete header
		del vmLines[-1] # Delete footer
		
		sep = re.compile(':[\s]+')
		vm_stats = {}

		for row in vmLines:
			element = sep.split(row)
			vm_stats[(element[0])] = int(element[1].strip('\.')) * 4096


		memory_dict['memfree'] =  vm_stats["Pages free"]/1024/1024 +vm_stats['Pages speculative']/1024/1024


		return memory_dict
	
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
				
				data[_name] = _volume

		return data


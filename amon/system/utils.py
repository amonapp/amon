import subprocess	
import sys
def get_disk_volumes():
		df = subprocess.Popen(['df','-h'], stdout=subprocess.PIPE, close_fds=True).communicate()[0]	
		
		volumes = df.split('\n')	
		volumes.pop(0)	# remove the header
		volumes.pop()

		volumes_list = []
		
		for volume in volumes:
			line = volume.split()
			if line[0].startswith('/'):
				volumes_list.append(line[0].replace('/dev/', ''))

		return volumes_list


def get_network_interfaces():
	if sys.platform == 'darwin':
		return False

	interfaces_info = open('/proc/net/dev' , 'r').readlines()

	interfaces_list = []
	# skip the header 
	for line in interfaces_info[2:]:
		interface, data = line.split(":")
		interface = interface.strip()
		if interface != 'lo':
			interfaces_list.append(interface)

	return interfaces_list

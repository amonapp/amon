import subprocess	
import sys
import calendar
import unicodedata
import re
from datetime import datetime

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


# Used in the collector, saves all the data in UTC
def unix_utc_now():
	d = datetime.utcnow()
	_unix = calendar.timegm(d.utctimetuple())

	return _unix

def slugify(string):

	"""
	Slugify a unicode string.

	"""

	return re.sub(r'[-\s]+', '-',
			unicode(
				re.sub(r'[^\w\s-]', '',
					unicodedata.normalize('NFKD', string)
					.encode('ascii', 'ignore'))
				.strip()
				.lower()))


def split_and_slugify(string, separator=":"):
	_string = string.strip().split(separator)
	
	if len(_string) == 2: # Only key, value
		data = {}
		key = slugify(unicode(_string[0]))
		
		try:
			if len(_string[1]) > 0:
				data[key] = str(_string[1].strip())
		except:
			pass

		return data
	
	else:
		return None
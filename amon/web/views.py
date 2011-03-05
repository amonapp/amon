from template import render
import cherrypy
from db import _conn
from utils import json_string_to_dict, json_list_to_dict

class Dashboard:

	@cherrypy.expose
	def index(self):
	
		# get redis server info
		try:
			connection = _conn.info()
		except:
			connection = False

		# get the information from the last check
		try:
			latest_check = _conn.zrange('amon_log', -1, -1)
			latest_check_dict = json_string_to_dict(latest_check[0])
		except:
			latest_check_dict = False

		return render(name="dashboard.html",
					  current_page='dashboard',
					  check=latest_check_dict,
					  connection=connection,
				)
	
class System:

	@cherrypy.expose
	def index(self):

		try:
			_log = _conn.zrange('amon_log', -1000, -1)
			log = json_list_to_dict(_log)
		except:
			log = False

		# Extract individual dictionaries
		if log != False:
			

			memory = []
			
			cpu = []
			loadavg = []
			
			network = []
			network_interfaces = []
			
			disk = []
			volumes = []
			
			
			for _dict in log:

				_dict['memory']['time'] = _dict['time']
				_dict['loadavg']['time'] = _dict['time']
				_dict['cpu']['time'] = _dict['time']
				_dict['network']['time'] = _dict['time']
				_dict['disk']['time'] = _dict['time']
				

				memory.append(_dict['memory'])
				loadavg.append(_dict['loadavg'])
				cpu.append(_dict['cpu'])
				network.append(_dict['network'])	
				disk.append(_dict['disk'])

				_interfaces = _dict['network'].keys()
				for interface in _interfaces:
					if interface not in network_interfaces and interface != 'time':
						network_interfaces.append(interface)
			
				_volumes = _dict['disk'].keys()
				for volume in _volumes:
					if volume not in volumes and volume != 'time':
						volumes.append(volume)
			

			return render(name='system.html',
						  current_page='system',
						  memory=memory,
						  cpu=cpu,
						  network=network,
						  network_interfaces=network_interfaces,
						  loadavg=loadavg,
						  volumes=volumes,
						  disk=disk)
		











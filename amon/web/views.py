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
	
	


class Node:

	@cherrypy.expose
	def index(self):

		try:
			_log = _conn.zrange('amon_log', -5, -1)
			log = json_list_to_dict(_log)
		except:
			log = False

		# Extract individual dictionaries
		if log != False:
			

			memory = []
			cpu = []
			network = []
			network_interfaces = []
			loadavg = []
			disk = []
			labels = []

			
			for _dict in log:
				memory.append(_dict['memory'])
				loadavg.append(_dict['loadavg'])
				cpu.append(_dict['cpu'])
				network.append(_dict['network'])	
				disk.append(_dict['disk'])
				labels.append(_dict['time'])

				_interfaces = _dict['network'].keys()
				for interface in _interfaces:
					if interface not in network_interfaces:
						network_interfaces.append(interface)
			
			return render(name='node.html',
						  memory=memory,
						  cpu=cpu,
						  network=network,
						  network_interfaces=network_interfaces,
						  loadavg=loadavg,
						  labels=labels,
						  disk=disk)
		











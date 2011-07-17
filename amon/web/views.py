from template import render
import cherrypy
from db import storage

class Dashboard:

	@cherrypy.expose
	def index(self):
	

		return render(name="dashboard.html",
					current_page='dashboard',
			)
	
class System:


	def __init__(self):
		self.system_collection = storage._get_system_collection()

	@cherrypy.expose
	def index(self):


		
		log = self.system_collection.find().limit(1).sort('time':1)
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
		


class Application(object):

	@cherrypy.expose
	def index(self):

		return render(name='application.html',
					 current_page='application')







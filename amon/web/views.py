from template import render
import cherrypy
from amon.backends.mongodb import MongoBackend
from pymongo import DESCENDING, ASCENDING 
from datetime import datetime, timedelta
from utils import datestring_to_unixtime, datetime_to_unixtime  
from amon.core import settings

class Base(object):

	def __init__(self):
		self.mongo = MongoBackend()


class Dashboard(Base):

	@cherrypy.expose
	def index(self):
		
		last_check = {}
		active_checks = settings.ACTIVE_CHECKS

		try:
			for check in active_checks:
				row = self.mongo.get_collection(check)
				last_check[check] = row.find(limit=1).sort('time', DESCENDING)[0]
		except Exception, e:
			last_check = False
			raise e

		return render(name="dashboard.html",
					current_page='dashboard',
					last_check=last_check
					)

class System(Base):

	def __init__(self):
		super(System, self).__init__()
		self.now = datetime.now()

		day = timedelta(hours=24)
		week = timedelta(days=7)
		month = timedelta(days=30)

		_yesterday = self.now - day
		_week_ago = self.now - week
		_month_ago = self.now - month

		self.yesterday = datetime_to_unixtime(_yesterday)
		self.week_ago = datetime_to_unixtime(_week_ago) 
		self.month_ago = datetime_to_unixtime(_month_ago) 

	def _get_active_tab(self, date_from):
		tabs = {'day': self.yesterday,
				'week' : self.week_ago,
				'month': self.month_ago
				}

		active_tab = False

		for key,value in tabs.iteritems():
			if date_from == value:
				active_tab = key

		if active_tab is False:
			active_tab = 'custom'

		return active_tab

	
	

	@cherrypy.expose
	def index(self, *args, **kwargs):

		date_from = kwargs.get('date_from', False)

		if date_from:
			date_from = datestring_to_unixtime(date_from)
		# Default - 24 hours period
		else:
			date_from = self.yesterday

		active_tab = self._get_active_tab(date_from)
		
		checks = {}
		active_checks = settings.ACTIVE_CHECKS
		try:
			for check in active_checks:
				row = self.mongo.get_collection(check)
				checks[check] = row.find({"time": {"$gte": date_from}}).sort('time', ASCENDING)
		except Exception, e:
			checks = False
			raise e

		if checks != False:
			#memory = []
			
			#cpu = []
			#loadavg = []
			
			#network = []
			#network_interfaces = []
			
			#disk = []
			#volumes = []
			
			
			#for _dict in log:

				#_dict['memory']['time'] = _dict['time']
				#_dict['loadavg']['time'] = _dict['time']
				#_dict['cpu']['time'] = _dict['time']
				#_dict['network']['time'] = _dict['time']
				#_dict['disk']['time'] = _dict['time']

				#memory.append(_dict['memory'])
				#loadavg.append(_dict['loadavg'])
				#cpu.append(_dict['cpu'])
				#network.append(_dict['network'])	
				#disk.append(_dict['disk'])

				#_interfaces = _dict['network'].keys()
				#for interface in _interfaces:
					#if interface not in network_interfaces and interface != 'time':
						#network_interfaces.append(interface)
			
				#_volumes = _dict['disk'].keys()
				#for volume in _volumes:
					#if volume not in volumes and volume != 'time':
						#volumes.append(volume)
			

			return render(name='system.html',
						  current_page='system',
						  checks=checks,
						  #memory=memory,
						  #cpu=cpu,
						  #network=network,
						  #network_interfaces=network_interfaces,
						  #loadavg=loadavg,
						  #volumes=volumes,
						  #disk=disk,
						  week_ago=self.week_ago,
						  month_ago=self.month_ago,
						  active_tab=active_tab
						  )
		
class Application(Base):

	@cherrypy.expose
	def index(self):

		return render(name='application.html',
					 current_page='application')







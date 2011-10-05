from views import Dashboard, System, Processes, Settings, Logs, Exceptions
from api import API
from settings import PROJECT_ROOT

#apps
root = Dashboard()
root.system = System()
root.processes = Processes()
root.settings = Settings()
root.logs = Logs()
root.exceptions = Exceptions()
root.api = API()


config = {	
			'/': 
			{
				'tools.staticdir.root': PROJECT_ROOT
			},
			'/media': 
			{
				'tools.staticdir.on' : True,
				'tools.staticdir.dir' : 'media',
				'tools.gzip.on' : True
			}
		}

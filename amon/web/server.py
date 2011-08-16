from views import Dashboard, System, Processes, Settings, Logs
from settings import PROJECT_ROOT

#apps
root = Dashboard()
root.system = System()
root.processes = Processes()
root.settings = Settings()
root.logs = Logs()


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

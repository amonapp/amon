import sys
import cherrypy
from views import Dashboard 
from settings import PROJECT_ROOT

#apps
root = Dashboard()


cherrypy.config.update({
	'server.socket_host': '127.0.0.1',
	'server.socket_port': 8080,
	})


config = {	
			'/': 
			{
				'tools.staticdir.root': PROJECT_ROOT
			},
			'/media': 
			{
				'tools.staticdir.on' : True,
				'tools.staticdir.dir' : 'media'
			}
		}

sys.path.append(PROJECT_ROOT) # add the current directory to the PYTHONPATH
cherrypy.quickstart(root, "/" ,  config=config)

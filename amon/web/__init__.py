import cherrypy
from views import Dashboard, System,  Application 
from settings import PROJECT_ROOT

#apps
root = Dashboard()
root.system = System()
root.application = Application()


cherrypy.config.update({
	'server.socket_host': '127.0.0.1',
	'server.socket_port': 2464,
	'engine.autoreload_on': False	
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

cherrypy.tree.mount(root, "/", config)


import cherrypy
from server import root, config
from cherrypy.process.plugins import Daemonizer

Daemonizer(cherrypy.engine).subscribe()  

cherrypy.config.update({
	'server.socket_host': '127.0.0.1',
	'server.socket_port': 2464,
	'engine.autoreload_on': False	
	})

cherrypy.tree.mount(root, "/", config)


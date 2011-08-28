import sys
import cherrypy
from settings import PROJECT_ROOT
from server import root, config


sys.path.append(PROJECT_ROOT) # add the current directory to the PYTHONPATH


cherrypy.config.update({
	'server.socket_host': '127.0.0.1',
	'server.socket_port': 2464,
	'engine.autoreload_on': True,
	})


cherrypy.tree.mount(root, "/", config)

cherrypy.engine.start()
cherrypy.engine.block()

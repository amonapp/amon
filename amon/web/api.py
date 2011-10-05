import cherrypy
from amon.api import exception as _exception

class API(object):
	@cherrypy.expose
	def log(self, *args, **kwargs):
		pass

	@cherrypy.expose
	def exception(self, *args, **kwargs):
		cl = cherrypy.request.headers['Content-Length']
		rawbody = cherrypy.request.body.read(int(cl))
		_exception(rawbody)


import cherrypy
from amon.api import exception as _exception
from amon.api import log as _log

class API(object):
	@cherrypy.expose
	@cherrypy.tools.json_in(content_type=[u'application/json', u'text/javascript', 'application/x-www-form-urlencoded'] )
	def log(self, *args, **kwargs):
		_log(cherrypy.request.json)

	@cherrypy.expose
	@cherrypy.tools.json_in(content_type=[u'application/json', u'text/javascript', 'application/x-www-form-urlencoded'] )
	def exception(self, *args, **kwargs):
		_exception(cherrypy.request.json)


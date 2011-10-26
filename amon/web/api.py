import cherrypy
from amon.api import exception as _exception
from amon.api import log as _log

class API(object):
	@cherrypy.expose
	@cherrypy.tools.json_in(content_type=[u'application/json', u'text/javascript', 'application/x-www-form-urlencoded'] )
	def log(self, *args, **kwargs):
		try:
			json_dict = cherrypy.request.json
		except:
			json_dict = None
			raise cherrypy.HTTPError(405, 'Only POST requests containing the following json dictionary - {"message": "", "level": ""}')

		if json_dict != None:
			_log(cherrypy.request.json)
	
	@cherrypy.expose
	@cherrypy.tools.json_in(content_type=[u'application/json', u'text/javascript', 'application/x-www-form-urlencoded'] )
	def exception(self, *args, **kwargs):
		try:
			json_dict = cherrypy.request.json
		except:
			json_dict = None
			raise cherrypy.HTTPError(405, 'Only POST requests containing the following json dictionary - data = {\
					"exception_class": "",\
					"message": "",\
					"url": "",\
					"backtrace": "",\
					"enviroment": "",\
					"data": ""}')

		if json_dict != None:
			_exception(cherrypy.request.json)


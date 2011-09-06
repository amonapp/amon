import traceback
import sys
from django.core.urlresolvers import resolve
from amon.api import exception
import json

class AmonMiddleware(object):

	def process_exception(self, request, exc):	
		_exception = {}
		_exception['url'] = request.build_absolute_uri()

		_exception.update(self.exception_info(exc, sys.exc_info()[2]))	
		_exception['data'] = self.request_info(request) # Additional data 
		
		exception(json.dumps(_exception))


	def exception_class(self, exception):
		"""Return a name representing the class of an exception."""

		cls = type(exception)
		if cls.__module__ == 'exceptions':  # Built-in exception.
			return cls.__name__
		return "%s.%s" % (cls.__module__, cls.__name__)	

	def request_info(self, request):

		"""
		Return a dictionary of information for a given request.

		This will be run once for every request.
		"""

		# We have to re-resolve the request path here, because the information
		# is not stored on the request.
		view, args, kwargs = resolve(request.path)
		for i, arg in enumerate(args):
			kwargs[i] = arg

		parameters = {}
		parameters.update(kwargs)
		parameters.update(request.POST.items())

		return {
				"request": {
					"session": dict(request.session),
					"remote_ip": request.META["REMOTE_ADDR"],
					"parameters": parameters,
					"action": view.__name__,
					"application": view.__module__,
					"request_method": request.method,
					}
				}

	def exception_info(self, exception, tb):
		backtrace = []
		for tb_part in traceback.format_tb(tb):
			backtrace.extend(tb_part.rstrip().splitlines())

		return {
					"message": str(exception),
					"backtrace": backtrace,
					"exception_class": self.exception_class(exception)
					}


from amon.web.views import Dashboard, System, Processes, Exceptions, Logs
from amon.web.settings import PROJECT_ROOT
from amon.web.api import ApiLogs, ApiException
import os
import tornado.web
import base64
import uuid
	
app_settings = {
	"static_path": os.path.join(PROJECT_ROOT, "media"),
	"debug": "True",
	"cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)  
}

handlers = [
	(r"/", Dashboard),
	(r"/system", System),
	(r"/processes", Processes),
	(r"/exceptions", Exceptions),
	(r"/logs", Logs),
	(r"/api/log", ApiLogs),
	(r"/api/exception", ApiException),
	(r"/media/(.*)", tornado.web.StaticFileHandler, {"path": app_settings['static_path']}),
]
application = tornado.web.Application(handlers, **app_settings)

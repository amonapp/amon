from amon.web.views import Dashboard, System, Processes, Exceptions, Logs
from amon.web.settings import PROJECT_ROOT
import os
import tornado.web
	
app_settings = {
	"static_path": os.path.join(PROJECT_ROOT, "media"),
	"debug": True
}

application = tornado.web.Application([
	(r"/", Dashboard),
	(r"/system", System),
	(r"/processes", Processes),
	(r"/exceptions", Exceptions),
	(r"/logs", Logs),
	(r"/media/(.*)", tornado.web.StaticFileHandler, {"path": app_settings['static_path']}),
])


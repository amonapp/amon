from amon.web.views.app import DashboardView, SystemView, ProcessesView, ExceptionsView, LogsView
from amon.web.views.auth import LoginView, CreateUserView, LogoutView
from amon.web.settings import PROJECT_ROOT
from amon.core import settings
from amon.web.views.api import ApiLogs, ApiException
import os.path
import tornado.web
	
app_settings = {
	"static_path": os.path.join(PROJECT_ROOT, "media"),
	"debug": "True",
	"cookie_secret": settings.SECRET_KEY
}

handlers = [
	# App
	(r"/", DashboardView),
	(r"/system", SystemView),
	(r"/processes", ProcessesView),
	(r"/exceptions", ExceptionsView),
	(r"/logs", LogsView),
	# Auth
	(r"/login", LoginView),
	(r"/logout", LogoutView),
	(r"/create_user", CreateUserView),
	# API
	(r"/api/log", ApiLogs),
	(r"/api/exception", ApiException),
	# Static
	(r"/media/(.*)", tornado.web.StaticFileHandler, {"path": app_settings['static_path']}),
]
application = tornado.web.Application(handlers, **app_settings)

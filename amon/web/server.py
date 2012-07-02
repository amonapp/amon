from amon.web.views.app import(
        DashboardView,
        SystemView,
        ProcessesView,
        ExceptionsView,
        LogsView,
        SettingsView,
        SettingsDeleteLogsView,
        SettingsDeleteExceptionsView,
        SettingsChangePasswordView)
from amon.web.views.auth import LoginView, CreateUserView, LogoutView
from amon.web.settings import PROJECT_ROOT
from amon.core import settings
from amon.web.views.api import ApiLogs, ApiException
import os.path
import tornado.web
import base64

login_url = "{0}:{1}/login".format(settings.WEB_APP['host'], settings.WEB_APP['port'])\
    if settings.PROXY is None else '/login'
    
app_settings = {
	"static_path": os.path.join(PROJECT_ROOT, "media"),
	"cookie_secret": base64.b64encode(settings.SECRET_KEY),
	"login_url" : login_url,
	"session": {"duration": 3600, "regeneration_interval": 240, "domain": settings.WEB_APP['host']}
}

handlers = [
	# App
	(r"/", DashboardView),
	(r"/system", SystemView),
	(r"/processes", ProcessesView),
	(r"/exceptions", ExceptionsView),
	(r"/logs", LogsView),
	(r"^/logs/(?P<page>\d+)$", LogsView),
	(r"^/settings", SettingsView),
	(r"^/settings/delete-logs$", SettingsDeleteLogsView),
    (r"^/settings/delete-exceptions$", SettingsDeleteExceptionsView),
    (r"^/settings/change-password$", SettingsChangePasswordView),
	# Auth
	(r"/login", LoginView),
	(r"/logout", LogoutView),
	(r"/create_user", CreateUserView),
	# API
	(r"/api/log/{0}".format(settings.SECRET_KEY), ApiLogs),
	(r"/api/exception/{0}".format(settings.SECRET_KEY), ApiException),
	# Static
	(r"/media/(.*)", tornado.web.StaticFileHandler, {"path": app_settings['static_path']})
]

application = tornado.web.Application(handlers, **app_settings)

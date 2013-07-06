import os.path
import tornado.web
from tornado.web import url
from amonone.web.settings import PROJECT_ROOT
from amonone.core import settings
from amonone.web.apps.dashboard.views import DashboardView
from amonone.web.apps.system.views import SystemView
from amonone.web.apps.processes.views import ProcessesView

from amonone.web.apps.alerts.views import (
	AlertsView,
	AddSystemAlertView,
	DeleteServerAlertView,
	AddProcessAlertView,
	DeleteProcessAlertView,
	MuteAlertView, 
	AlertHistoryView,
	ClearAlertHistoryView,
	EditServerAlertView,
	EditProcessAlertView
	)

from amonone.web.apps.settings.views.data import (
		DataView,
		DataDeleteSystemCollectionView,
		DataDeleteProcessCollectionView,
		DataCleanupSystemView,
		DataCleanupProcessView
)

from amonone.web.apps.settings.views.email import (
		EmailView,
		EmailUpdateView,
		EmailTestView,
		EmailAddRecepient,
		EmailEditRecepientView,
		EmailDeleteRecepientView
)

from amonone.web.apps.settings.views.users import (
		UpdatePasswordUserView
)

from amonone.web.apps.settings.views.sms import(
		SMSView,
		SMSUpdateView,
		SMSTestView,
		SMSAddRecepient,
		SMSEditRecepientView,
		SMSDeleteRecepientView
)

from amonone.web.apps.auth.views import LoginView, CreateInitialUserView, LogoutView

	
app_settings = {
	"static_path": os.path.join(PROJECT_ROOT, "media"),
	"cookie_secret": settings.SECRET_KEY,
	"login_url" : "{0}:{1}/login".format(settings.WEB_APP['host'], settings.WEB_APP['port']),
	"session": {"duration": 3600, "regeneration_interval": 240, "domain": settings.WEB_APP['host']}
}


handlers = [
	# App
	url(r"/", DashboardView, name='dashboard'),
	url(r"/system", SystemView, name='system'),
	url(r"/processes", ProcessesView, name='processes'),
	# Alerts
	url(r"^/alerts$", AlertsView, name='alerts'),
	url(r"^/alerts/system/add$", AddSystemAlertView, name='add_server_alert'),
	url(r"^/alerts/system/delete/(?P<param>\w+)$", DeleteServerAlertView, name='delete_server_alert'),
	url(r"^/alerts/process/add$", AddProcessAlertView, name='add_process_alert'),
	url(r"^/alerts/process/delete/(?P<param>\w+)$", DeleteProcessAlertView, name='delete_proces_alert'),
	url(r"^/alerts/mute/(?P<rule_id>\w+)$", MuteAlertView, name='mute_alert'),
	url(r"^/alerts/history/(?P<alert_id>\w+)$", AlertHistoryView, name='alert_history'),
	url(r"^/alerts/clear_history/(?P<alert_id>\w+)$", ClearAlertHistoryView, name='alert_clear_history'),
	url(r"^/alerts/edit/server/(?P<alert_id>\w+)$", EditServerAlertView, name='edit_server_alert'),
	url(r"^/alerts/edit/process/(?P<alert_id>\w+)$", EditProcessAlertView, name='edit_process_alert'),
	# Email settings
	url(r"^/settings/email$", EmailView, name='settings_email'),
	url(r"^/settings/email/edit$", EmailUpdateView, name='update_email'),
	url(r"^/settings/email/add_recepient$", EmailAddRecepient, name='email_add_recepient'),
	url(r"^/settings/email/recepients/edit/(?P<recepient_id>[-\w]+)$", EmailEditRecepientView, name='email_edit_recepient'),
	url(r"^/settings/email/recepients/delete/(?P<recepient_id>[-\w]+)$", EmailDeleteRecepientView, name='email_delete_recepient'),
	url(r"^/settings/email/test$", EmailTestView, name='test_email'),
	# SMS settings
	url(r"^/settings/sms$", SMSView, name='settings_sms'),
	url(r"^/settings/sms/edit$", SMSUpdateView, name='sms_update'),
	url(r"^/settings/sms/add_recepient$", SMSAddRecepient, name='sms_add_recepient'),
	url(r"^/settings/sms/recepients/edit/(?P<recepient_id>[-\w]+)$", SMSEditRecepientView, name='sms_edit_recepient'),
	url(r"^/settings/sms/recepients/delete/(?P<recepient_id>[-\w]+)$", SMSDeleteRecepientView, name='sms_delete_recepient'),
	url(r"^/settings/sms/test$", SMSTestView, name='sms_test'),
	# Data settings
	url(r"^/settings/data$", DataView, name='settings_data'),
	# Users settings
	url(r"^/settings/users/update_password/(?P<id>\w+)$", UpdatePasswordUserView, name='update_password'),
	# Auth
	url(r"/login", LoginView, name='login'),
	url(r"/logout", LogoutView, name='logout'),
	url(r"/create_user", CreateInitialUserView, name='create_user'),
	# Static
	(r"/media/(.*)", tornado.web.StaticFileHandler, {"path": app_settings['static_path']}),
]
application = tornado.web.Application(handlers, **app_settings)

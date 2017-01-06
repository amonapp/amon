from amon.apps.alerts.models.alerts import AlertsModel
from amon.apps.alerts.models.alertshistory import AlertHistoryModel
from amon.apps.alerts.models.mute import AlertMuteServersModel
from amon.apps.alerts.models.api import AlertsAPIModel

alerts_model = AlertsModel()
alerts_history_model = AlertHistoryModel()
alert_mute_servers_model = AlertMuteServersModel()
alerts_api_model = AlertsAPIModel()
from django.conf.urls import url

from amon.apps.alerts.views import alerts as alert_views
from amon.apps.alerts.views import pause as pause_views
from amon.apps.alerts.views import healthchecks as healthcheck_views
from amon.apps.alerts import api

urlpatterns = [
    url(
        r'^$',
        alert_views.all,
        name='alerts'
    ),
    url(
        r'^clear_triggers/(?P<alert_id>\w+)/$',
        alert_views.clear_triggers,
        name='alerts_clear_triggers'
    ),

    url(
        r'^delete/(?P<alert_id>\w+)/$',
        alert_views.delete_alert,
        name='delete_alert'
    ),

    url(
        r'^add/$',
        alert_views.add_alert,
        name='add_alert'
    ),

    url(
        r'^edit/(?P<alert_id>\w+)/$',
        alert_views.edit_alert,
        name='edit_alert'
    ),
    url(
        r'^history/(?P<alert_id>\w+)/$',
        alert_views.history,
        name='global_alert_history'
    ),

    url(
        r'^history/system/(?P<alert_id>\w+)/$',
        alert_views.history_system,
        name='system_alert_history'
    ),
    # Ajax
    url(
        r'^a/history/(?P<alert_id>\w+)/$',
        alert_views.ajax_alert_triggers,
        name='ajax_alert_history'
    ),

    # Mute
    url(
        r'^pause/global/$',
        pause_views.mute_servers,
        name='alerts_mute_servers'
    ),
    url(
        r'^unpause/server/(?P<mute_id>\w+)$',
        pause_views.unmute_server,
        name='alerts_unmute_server'
    ),

    url(
        r'^pause/id/(?P<alert_id>\w+)/$',
        pause_views.mute,
        name='mute_alert'
    ),

    url(
        r'^pause_all/$',
        pause_views.mute_all,
        name='mute_all_alerts'
    ),

    # HealthCheck alerts
    url(
        r'^add/healthcheck/$',
        healthcheck_views.add_alert,
        name='add_healthcheck_alert'
    ),

    url(
        r'^edit/healthcheck/(?P<alert_id>\w+)/$',
        healthcheck_views.edit_alert,
        name='edit_healthcheck_alert'
    ),

]

ajax_patterns = [
    url(
        r'^a/get_metrics/$',
        api.ajax_get_metrics,
        name='api_alerts_get_metrics'
    ),
    url(
        r'^a/get_health_check_commands/$',
        api.ajax_get_health_check_commands,
        name='api_alerts_get_health_check_commands'
    ),
    url(
        r'^a/get_health_check_params_for_command/$',
        api.ajax_get_health_check_get_params_for_command,
        name='api_alerts_get_health_check_params_for_command'
    )
]

urlpatterns = urlpatterns + ajax_patterns
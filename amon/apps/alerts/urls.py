from django.conf.urls import patterns,url


urlpatterns = patterns('amon.apps.alerts.views',
    url(
        
        r'^$',
        'alerts.all' ,
         name='alerts'
    ),
    url(
        r'^clear_triggers/(?P<alert_id>\w+)/$',
        'alerts.clear_triggers' ,
         name='alerts_clear_triggers'
     ),

    url(
        r'^delete/(?P<alert_id>\w+)/$',
        'alerts.delete_alert' ,
         name='delete_alert'
     ),

    url(
        r'^add/$',
        'alerts.add_alert' ,
         name='add_alert'
     ),

    url(
        r'^edit/(?P<alert_id>\w+)/$',
        'alerts.edit_alert' ,
         name='edit_alert'
     ),
    url(
        r'^history/(?P<alert_id>\w+)/$',
        'alerts.history' ,
         name='global_alert_history'
     ),

    url(
        r'^history/system/(?P<alert_id>\w+)/$',
        'alerts.history_system' ,
         name='system_alert_history'
     ),
    # Ajax
    url(
        r'^a/history/(?P<alert_id>\w+)/$',
        'alerts.ajax_alert_triggers' ,
         name='ajax_alert_history'
     ),

    # Mute 
    url(
        r'^pause/global/$',
        'pause.mute_servers' ,
         name='alerts_mute_servers'
     ),
    url(
        r'^unpause/server/(?P<mute_id>\w+)$',
        'pause.unmute_server' ,
         name='alerts_unmute_server'
     ),

    url(
        r'^pause/id/(?P<alert_id>\w+)/$',
        'pause.mute' ,
         name='mute_alert'
     ),

    url(
        r'^pause_all/$',
        'pause.mute_all' ,
         name='mute_all_alerts'
     ),

    # HealthCheck alerts
    url(
        r'^add/healthcheck/$',
        'healthchecks.add_alert' ,
         name='add_healthcheck_alert'
     ),

    url(
        r'^edit/healthcheck/(?P<alert_id>\w+)/$',
        'healthchecks.edit_alert' ,
         name='edit_healthcheck_alert'
     ),

)

ajax_patterns = patterns('amon.apps.alerts.api',

    url(
        r'^a/get_metrics/$',
        'ajax_get_metrics',
        name='api_alerts_get_metrics'
    ),
    url(
        r'^a/get_health_check_commands/$',
        'ajax_get_health_check_commands',
        name='api_alerts_get_health_check_commands'
    ),
    url(
        r'^a/get_health_check_params_for_command/$',
        'ajax_get_health_check_get_params_for_command',
        name='api_alerts_get_health_check_params_for_command'
    )
)
urlpatterns = urlpatterns+ajax_patterns
from django.conf.urls import patterns, url


urlpatterns = patterns('',
    # AJAX
    url(r'^a/get_ignored_data_for_timestamp/$','amon.apps.processes.views.ajax_get_ignored_data_for_timestamp', name='ajax_get_process_ignored_data_for_timestamp'),
    url(r'^a/get_data_for_timestamp/$','amon.apps.processes.views.ajax_get_data_for_timestamp', name='ajax_get_process_data_for_timestamp'),
    url(r'^a/monitor/$','amon.apps.processes.views.ajax_monitor_process', name='ajax_monitor_process'),
    url(r'^a/get_data_after/$','amon.apps.processes.views.ajax_get_data_after', name='ajax_get_process_data_after'),
    url(r'^(?P<server_id>\w+)/$','amon.apps.processes.views.view_process' , name='view_process'),
)
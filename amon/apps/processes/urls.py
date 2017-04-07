from django.conf.urls import url

from amon.apps.processes import views


urlpatterns = (
    # AJAX
    url(r'^a/get_ignored_data_for_timestamp/$', views.ajax_get_ignored_data_for_timestamp, name='ajax_get_process_ignored_data_for_timestamp'),
    url(r'^a/get_data_for_timestamp/$', views.ajax_get_data_for_timestamp, name='ajax_get_process_data_for_timestamp'),
    url(r'^a/monitor/$', views.ajax_monitor_process, name='ajax_monitor_process'),
    url(r'^a/get_data_after/$', views.ajax_get_data_after, name='ajax_get_process_data_after'),
    url(r'^(?P<server_id>\w+)/$', views.view_process , name='view_process'),
)
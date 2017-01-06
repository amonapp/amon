from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # AJAX
    url(r'^ajax_get_gauge_data_after/$','amon.apps.plugins.views.ajax_get_gauge_data_after', name='ajax_get_gauge_data_after'),
    url(r'^view/(?P<server_id>\w+)$', 'amon.apps.plugins.views.view_plugins' , name='view_plugins'),
)
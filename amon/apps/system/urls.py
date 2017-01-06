from django.conf.urls import patterns, url


urlpatterns = patterns('',

    # AJAX
    url(r'^a/get_data_after/$','amon.apps.system.api.ajax_get_data_after', name='ajax_get_data_after'),

    # Views
    url(r'^(?P<server_id>\w+)/$','amon.apps.system.views.system_view', name='server_system'),
)
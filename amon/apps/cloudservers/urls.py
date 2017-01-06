from django.conf.urls import patterns, url

urlpatterns = patterns('amon.apps.cloudservers.views',
    url(r'^$', 'index', name='cloudservers'),
    url(r'^(?P<provider_id>\w+)/$', 'edit', name='cloudservers_edit'),
    url(r'^add/(?P<provider_id>\w+)/$', 'add', name='cloudservers_add'),
    url(r'^edit/(?P<provider_id>\w+)/(?P<credentials_id>\w+)/$', 'edit', name='cloudservers_edit'),
    url(r'^delete/(?P<provider_id>\w+)/(?P<credentials_id>\w+)/$', 'delete', name='cloudservers_delete'),
    url(r'^delete_confirmed/(?P<provider_id>\w+)/(?P<credentials_id>\w+)/$', 'delete_confirmed', name='cloudservers_delete_confirmed'),
)


api_patterns = patterns('amon.apps.cloudservers.api',

    url(
        r'^a/get_amazon_regions$',
        'ajax_get_amazon_regions',
        name='api_cloudservers_get_amazon_regions'
    ), 

    url(
        r'^a/get_rackspace_regions$',
        'ajax_get_rackspace_regions',
        name='api_cloudservers_get_rackspace_regions'
    ), 

)


urlpatterns = urlpatterns+api_patterns
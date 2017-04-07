from django.conf.urls import url

from amon.apps.cloudservers import views
from amon.apps.cloudservers import api

urlpatterns = [
    url(r'^$', views.index, name='cloudservers'),
    url(r'^(?P<provider_id>\w+)/$', views.edit, name='cloudservers_edit'),
    url(r'^add/(?P<provider_id>\w+)/$', views.add, name='cloudservers_add'),
    url(r'^edit/(?P<provider_id>\w+)/(?P<credentials_id>\w+)/$', views.edit, name='cloudservers_edit'),
    url(r'^delete/(?P<provider_id>\w+)/(?P<credentials_id>\w+)/$', views.delete, name='cloudservers_delete'),
    url(r'^delete_confirmed/(?P<provider_id>\w+)/(?P<credentials_id>\w+)/$', views.delete_confirmed, name='cloudservers_delete_confirmed'),
]


api_patterns = [

    url(
        r'^a/get_amazon_regions$',
        api.ajax_get_amazon_regions,
        name='api_cloudservers_get_amazon_regions'
    ),

    url(
        r'^a/get_rackspace_regions$',
        api.ajax_get_rackspace_regions,
        name='api_cloudservers_get_rackspace_regions'
    ),

]


urlpatterns = urlpatterns + api_patterns